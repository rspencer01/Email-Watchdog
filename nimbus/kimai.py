"""Collate information from kimai and present it in a nice format."""
import datetime
import tempfile

import kimai_python
import plotly.express as px

import nimbus.notifications

CONFIGURATION = kimai_python.Configuration()
CONFIGURATION.host = "https://kimai.robertandrewspencer.com"
CONFIGURATION.api_key["X-AUTH-USER"] = "robert"
CONFIGURATION.api_key["X-AUTH-TOKEN"] = "foo2bard"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

CLIENT = kimai_python.ApiClient(CONFIGURATION)

users = kimai_python.UserApi(CLIENT)
timesheets = kimai_python.TimesheetApi(CLIENT)
activities = kimai_python.ActivityApi(CLIENT)
projects = kimai_python.ProjectApi(CLIENT)


def today():
    times_today = timesheets.api_timesheets_get(
        begin=datetime.date.today().strftime(TIME_FORMAT)
    )
    activities_performed = {session.activity for session in times_today}
    activities_d = dict(
        [(i, activities.api_activities_id_get(i)) for i in activities_performed]
    )
    projects_performed = set([i.project for i in activities_d.values()])
    projects_d = dict(
        [(i, projects.api_projects_id_get(i)) for i in projects_performed]
    )
    customers = set([i.parent_title for i in projects_d.values()])
    time_spent_per_activity = [
        (
            activity,
            sum(
                [
                    session.duration
                    for session in times_today
                    if session.activity == activity
                ]
            )
            // 60,
        )
        for activity in activities_performed
    ]
    time_spent_per_project = [
        (
            project,
            sum(
                [
                    i[1]
                    for i in time_spent_per_activity
                    if activities_d[i[0]].project == project
                ]
            ),
        )
        for project in projects_performed
    ]
    time_spent_per_customer = [
        (
            customer,
            sum(
                [
                    i[1]
                    for i in time_spent_per_project
                    if projects_d[i[0]].parent_title == customer
                ]
            ),
        )
        for customer in customers
    ]
    time_spent_per_customer.sort(key=lambda x: x[::-1])
    time_spent_per_project.sort(key=lambda x: x[::-1])
    time_spent_per_activity.sort(key=lambda x: x[::-1])
    times = []
    for customer, _ in time_spent_per_customer:
        for project, t in time_spent_per_project:
            if projects_d[project].parent_title != customer:
                continue
            times.append((project, projects_d[project].name, t))
    cols = dict([(i, projects_d[i].color) for i in projects_performed])
    times = [[i[j] for i in times] for j in range(3)]
    # TODO(robert) use sunburst charts
    fig = px.pie(
        names=times[1], values=times[2], color=times[0], color_discrete_map=cols
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        showlegend=False, margin=dict(l=20, r=20, t=20, b=20), width=500, height=500
    )
    nimbus.notifications.add_notification(
        "Your timechart for today", False, fig.to_image(format="jpg")
    )
