from django.shortcuts import render
from loguru import logger
import csv
from django.http import HttpResponse
from .models import TotalByDay, Video, Report
from django.shortcuts import redirect
from insight_app.libs.plot_data import Plotter
import pandas as pd


def upload_csv(request):
    if request.method == "POST":
        files = [
            request.FILES["videos"],
            request.FILES["trending"],
            request.FILES["total"],
            request.FILES["gender"],
            request.FILES["followers"],
            request.FILES["territory"],
            request.FILES["activity"],
        ]

        dataframes = [pd.read_csv(file) for file in files]
        # add insert column (on 4 index) to the videos video_views_within_7_days = 0
        report = Report.from_csvs(
            videos=dataframes[0],
            trending=dataframes[1],
            total=dataframes[2],
            gender=dataframes[3],
            followers=dataframes[4],
            territory=dataframes[5],
            activity=dataframes[6],
            title=request.POST["title"],
            description=request.POST["description"],
        )
        report.save()

        return redirect("analysis")

    return render(request, "home.html")


# Create your views here.
def home(request):
    return render(request, "home.html")


def analysis(request):
    report = Report.objects.last()
    plotter = Plotter(report)
    plots = plotter()
    return render(request, "analysis.html", {"plot_data": plots, "report": report})
