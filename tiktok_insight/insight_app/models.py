from django.db import models
from datetime import datetime
from loguru import logger
from csv import reader
import pandas as pd
import pycountry
import numpy as np

# generator chain
from itertools import chain


class TotalByDay(models.Model):
    date = models.DateField(primary_key=True)
    video_views = models.IntegerField()
    profile_views = models.IntegerField()
    likes = models.IntegerField()
    comments = models.IntegerField()
    shares = models.IntegerField()
    unique_viewers = models.IntegerField()
    report = models.ForeignKey("Report", on_delete=models.CASCADE)

    @classmethod
    def from_csv(cls, row, report):
        (
            date_str,
            video_views,
            profile_views,
            likes,
            comments,
            shares,
            unique_viewers,
        ) = row
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return cls(
            date=date,
            video_views=int(video_views),
            profile_views=int(profile_views),
            likes=int(likes),
            comments=int(comments),
            shares=int(shares),
            unique_viewers=int(unique_viewers),
            report=report,
        )

    def __str__(self):
        return f"{self.date} views: {self.video_views}"


class Video(models.Model):
    time = models.DateTimeField()
    video_title = models.CharField(max_length=255)
    video_link = models.URLField(max_length=500)
    post_time = models.DateTimeField(primary_key=True)
    video_views_within_7_days = models.IntegerField()
    total_likes = models.IntegerField()
    total_comments = models.IntegerField()
    total_shares = models.IntegerField()
    total_views = models.IntegerField()
    tags = models.TextField()
    report = models.ForeignKey("Report", on_delete=models.CASCADE)

    @classmethod
    def from_csv(cls, row, report):
        row = row.tolist()
        if len(row) == 8:
            row.insert(4, 0)
        if len(row) != 9:
            raise ValueError(f"Row has {len(row)} columns, expected 9: {row}")
        (
            time_str,
            video_title,
            video_link,
            post_time_str,
            video_views_within_7_days,
            total_likes,
            total_comments,
            total_shares,
            total_views,
        ) = row
        logger.info(f"Creating video from {row}")
        time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        post_time = datetime.strptime(post_time_str, "%Y-%m-%d %H:%M")
        tags = " ".join(tag.strip() for tag in video_title.split("#")[1:])
        title = video_title.split("#")[0].strip()
        if cls.objects.filter(post_time=post_time, report=report).exists():
            logger.warning(f"Video with post_time {post_time} already exists")
            obj = cls.objects.get(post_time=post_time, report=report)
            if video_views_within_7_days > 0:
                obj.video_views_within_7_days = video_views_within_7_days
            return obj
        try:
            total_views = int(total_views)
        except ValueError:
            logger.warning(f"Total views {total_views} is not a number")
            total_views = 0

        return cls(
            time=time,
            video_title=title,
            video_link=video_link,
            post_time=post_time,
            total_likes=int(total_likes),
            video_views_within_7_days=int(video_views_within_7_days),
            total_comments=int(total_comments),
            total_shares=int(total_shares),
            total_views=total_views,
            tags=tags,
            report=report,
        )

    def __str__(self):
        return f"{self.video_title} - {self.post_time} ({self.total_views})"

    @property
    def likes_to_views_ratio(self):
        return self.total_likes * 100 / self.total_views

    @property
    def comments_to_views_ratio(self):
        return self.total_comments * 100 / self.total_views

    @property
    def shares_to_views_ratio(self):
        return self.total_shares * 100 / self.total_views


class Report(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def total_views(self):
        return sum([entry.video_views for entry in self.totalbyday_set.all()])

    @property
    def total_likes(self):
        return sum([entry.likes for entry in self.totalbyday_set.all()])

    @property
    def total_comments(self):
        return sum([entry.comments for entry in self.totalbyday_set.all()])

    @property
    def total_shares(self):
        return sum([entry.shares for entry in self.totalbyday_set.all()])

    @property
    def total_unique_viewers(self):
        return sum([entry.unique_viewers for entry in self.totalbyday_set.all()])

    @property
    def avg_likes_to_view_ratios(self):
        return np.mean([video.likes_to_views_ratio for video in self.video_set.all()])

    @property
    def total_videos(self):
        return self.video_set.count()

    @property
    def total_territories(self):
        return self.territory_set.count()

    @property
    def most_popular_country(self):
        terr = self.territory_set.all()
        return max(terr, key=lambda x: x.distribution)

    @classmethod
    def from_csvs(
        cls,
        total: pd.DataFrame,
        trending: pd.DataFrame,
        videos: pd.DataFrame,
        gender: pd.DataFrame,
        territory: pd.DataFrame,
        followers: pd.DataFrame,
        activity: pd.DataFrame,
        title: str,
        description: str,
    ):
        report = cls.objects.create(title=title, description=description)

        def create_instances(df, model):
            for _, row in df.iterrows():
                instance = model.from_csv(row, report)
                instance.save()

        create_instances(total, TotalByDay)
        create_instances(videos, Video)
        create_instances(trending, Video)
        print(pd.concat([videos, trending]))
        create_instances(gender, GenderDistribution)
        create_instances(territory, Territory)
        create_instances(followers, TotalFollowers)
        create_instances(activity, FollowersActivity)

        return report

    def __str__(self):
        return self.title


class Territory(models.Model):
    country = models.CharField(max_length=100, help_text="Full Country name")
    distribution = models.FloatField()
    report = models.ForeignKey("Report", on_delete=models.CASCADE)

    @classmethod
    def from_csv(cls, row, report):
        country_code = row[0]

        country_name = pycountry.countries.get(alpha_2=country_code).name
        distribution = row[1]
        distribution = float(distribution.strip("%")) / 100
        return cls.objects.create(
            country=country_name, distribution=distribution, report=report
        )

    def __str__(self):
        return f"{self.country} distribution: {self.distribution}"


class TotalFollowers(models.Model):
    date = models.DateField(primary_key=True)
    followers = models.IntegerField(null=True, blank=True)
    difference = models.IntegerField(null=True, blank=True)
    report = models.ForeignKey("Report", on_delete=models.CASCADE)

    @classmethod
    def from_csv(cls, row, report):
        date_str, followers, difference = row
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        try:
            followers = int(followers)
        except (ValueError, TypeError):
            followers = 0

        try:
            difference = int(difference)
        except (ValueError, TypeError):
            difference = 0
        return cls(date=date, followers=followers, difference=difference, report=report)

    def __str__(self):
        return f"{self.date} followers: {self.followers}"


class GenderDistribution(models.Model):
    gender = models.CharField(max_length=20)
    distribution = models.FloatField()
    report = models.ForeignKey("Report", on_delete=models.CASCADE)

    @classmethod
    def from_csv(cls, row, report):
        gender, distribution = row
        distribution = float(distribution.strip("%")) / 100
        return cls(gender=gender, distribution=distribution, report=report)

    def __str__(self):
        return f"{self.gender} distribution: {self.distribution}"


class FollowersActivity(models.Model):
    date = models.DateField()
    hour = models.IntegerField()
    active_followers = models.IntegerField()
    report = models.ForeignKey("Report", on_delete=models.CASCADE)

    @classmethod
    def from_csv(cls, row, report):
        date_str, hour, active_followers = row
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        hour = int(hour)
        active_followers = int(active_followers)
        return cls(
            date=date, hour=hour, active_followers=active_followers, report=report
        )

    def __str__(self):
        return (
            f"{self.date} hour: {self.hour} active followers: {self.active_followers}"
        )
