import inspect
from insight_app.models import (
    TotalByDay,
    Video,
    Report,
    GenderDistribution,
    Territory,
    TotalFollowers,
    FollowersActivity,
)
from typing import Any
from loguru import logger
import json
from itertools import dropwhile
from collections import defaultdict


class Plotter:

    def __init__(self, report: Report) -> None:
        self.report = report
        self.total_by_day = TotalByDay.objects.filter(report=report)
        self.videos = Video.objects.filter(report=report)
        self.genders = GenderDistribution.objects.filter(report=report)
        self.territories = Territory.objects.filter(report=report)
        self.followers = TotalFollowers.objects.filter(report=report)
        self.best_upload_hour = None
        self.activity = FollowersActivity.objects.filter(report=report)
        logger.info(f"Plotter initialized with {self.report}")

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        plot_methods = [
            method
            for method in inspect.getmembers(self, predicate=inspect.ismethod)
            if method[0].startswith("plot")
        ]

        data = {
            method[0].split("plot_")[1]: json.dumps(method[1]())
            for method in plot_methods
        }
        data["best_upload_hour"] = self.best_upload_hour
        logger.info(f"Plotter called with {data}")
        return data

    def plot_total_by_day(self, cut_first_le: int = 300) -> dict:
        # Convert QuerySet to list to allow slicing
        total_by_day = list(self.total_by_day)
        total_by_day = list(
            dropwhile(lambda entry: entry.video_views < cut_first_le, total_by_day)
        )

        x = [str(entry.date) for entry in total_by_day]
        y = [entry.video_views for entry in total_by_day]
        videos_date = [str(entry.post_time.date()) for entry in self.videos]
        videos_views = [entry.total_views for entry in self.videos]
        videos_name = [entry.video_title[:20] for entry in self.videos]
        return {
            "date": x,
            "views": y,
            "videos": {
                "date": videos_date,
                "views": videos_views,
                "name": videos_name,
            },
        }

    def plot_genders(self) -> dict:
        genders = [entry.gender for entry in self.genders]
        total = self.followers.last().followers / 100
        distributions = [round(entry.distribution * total, 2) for entry in self.genders]
        return {
            "genders": genders,
            "distributions": distributions,
        }

    def plot_followers(self, cut_first_le=20) -> dict:
        follower_data = list(self.followers)

        # get first day with more then cut_first_le followers
        total = next(
            (
                i
                for i, entry in enumerate(follower_data)
                if entry.followers > cut_first_le
            ),
            0,
        )

        date = [str(entry.date) for entry in follower_data[total:]]
        followers = [entry.followers for entry in follower_data[total:]]
        difference = [entry.difference for entry in follower_data[total:]]
        return {
            "date": date,
            "followers": followers,
            "difference": difference,
        }

    def plot_regions(self) -> dict:
        regions = [entry.country for entry in self.territories]
        total = self.followers.last().followers / 100
        distributions = [
            round(entry.distribution * (total), 2) for entry in self.territories
        ]
        return {
            "regions": regions,
            "distributions": distributions,
        }

    def plot_followers_activity_by_hour(self, min_active_time=3) -> dict:
        followers_by_hour = defaultdict(list)

        for entry in self.activity:
            followers_by_hour[entry.hour].append(entry.active_followers)

        hours = list(followers_by_hour.keys())
        avg_followers = [
            sum(values) / len(values) for values in followers_by_hour.values()
        ]

        # Find the starting hour of the best couple of hours
        best_upload_hour = max(
            range(len(avg_followers) - min_active_time + 1),
            key=lambda i: sum(avg_followers[i : i + min_active_time]),
        )
        self.best_upload_hour = hours[best_upload_hour]
        return {
            "hours": hours,
            "avg_followers": avg_followers,
        }
