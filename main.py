import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import pandas as pd
import requests
import urllib3
import seaborn as sns
from pandas import json_normalize
import datetime as dt
import pytz
import login as login

sns.set_theme()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

auth_url = 'https://www.strava.com/oauth/token'
activities_url = 'https://www.strava.com/api/v3/athlete/activities'

payload = {
    'client_id': f'{login.client_id}',
    'client_secret': f'{login.client_secret}',
    'refresh_token': f'{login.refresh_token}',
    'grant_type': 'refresh_token',
    'f': 'json'
}

print('Requesting Token...\n')
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']

header = {'Authorization': 'Bearer ' + access_token}


# The Strava API only supports 200 results per page. This function loops through each page until new_results is empty.
def loop_through_pages(page):
    # start at page ...
    page = page
    # set new_results to True initially
    new_results = True
    # create an empty array to store our combined pages of data in
    data = []
    while new_results:
        # Give some feedback
        print(f'You are requesting page {page} of your activities data ...')
        # request a page + 200 results
        get_strava = requests.get(activities_url, headers=header, params={'per_page': 200, 'page': f'{page}'}).json()
        # save the response to new_results to check if its empty or not and close the loop
        new_results = get_strava
        # add our responses to the data array
        data.extend(get_strava)
        # increment the page
        page += 1
    # return the combine results of our get requests
    return data


def meters_to_miles():
    activities.distance = activities.distance / 1609


def mph_convert():
    activities.average_speed = activities.average_speed * 2.237


def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{:.1f}%\n({v:d})'.format(pct, v=val)

    return my_format


# call the function to loop through our strava pages and set the starting page at 1
my_dataset = loop_through_pages(1)
# Filter out any activities that aren't runs.
my_cleaned_dataset = []
for activities in my_dataset:
    if activities['type'] == 'Run':
        my_cleaned_dataset.append(activities)
activities = json_normalize(my_cleaned_dataset)
meters_to_miles()
mph_convert()
df = pd.DataFrame(data=activities)

# df['total_runs'] = df.groupby('name').transform('count')
# print(df.head())
# print(df.columns)
# df2 = df.groupby('name').agg({'distance': 'sum'}).reset_index()
# print(df2.head())
# fig, ax = plt.subplots(figsize=(8, 8))
# ax.pie(df2.distance, autopct=autopct_format(df2.distance))
# ax.legend(labels=df2.name, loc='best', bbox_to_anchor=(.3, .3))
# ax.set_title('Percentage of Total Runs')
# plt.savefig('imgs/total_runs_pie_chart.png', bbox_inches='tight', dpi=200)

df_run = df[df['sport_type'] == 'Run']

miles_to_km = 1.60934

df_run['distance_km'] = df_run['distance'] * miles_to_km
df_run['average_speed_km'] = df_run['average_speed'] * miles_to_km


print(df_run[['name', 'distance', 'moving_time', 'type', 'sport_type', 'workout_type', 'kudos_count', 'athlete_count', 'average_heartrate', 'start_date', 'start_date_local']].head())

last_workout = pd.to_datetime(df_run['start_date_local'].max(), utc=True)
last_workout_formatted = last_workout.strftime('%B %d %Y %H:%M')

now = dt.datetime.now(pytz.utc) + pd.Timedelta(hours=2)
formatted_now = now.strftime('%Y-%m-%d %H:%M')

time_since_last_workout = now - last_workout

days_since_latest_value = time_since_last_workout.days
hours_since_latest_value = time_since_last_workout.seconds // 3600

print(days_since_latest_value)

if days_since_latest_value > 0:
    print(f'Your latest run workout was at {last_workout_formatted} which is {days_since_latest_value} days and {hours_since_latest_value} hours ago')
else:
    print(f'Your latest run workout was at {last_workout_formatted} which is {hours_since_latest_value} hours ago')


# scatter plot of heartrate and pace
fig3, ax3 = plt.subplots(figsize=(8, 8))
ax3.scatter(df_run.average_heartrate, df_run.average_speed_km)
ax3.set_title('Average Speed by Heartrate')
# ax3.set_xticks(df.distance, df2.avg_pace_labels, rotation=90)
ax3.set_xlabel('Average Heartrate')
ax3.set_ylabel('Average Speed (km/h)')
# ax3.invert_xaxis()
ax3.xaxis.set_minor_locator(plticker.LinearLocator())
fig3.tight_layout()
plt.savefig('imgs/avg_pace_scatter_plot.png', bbox_inches='tight', dpi=200)


# print(now)
# print(days_since_latest_value)
# print(hours_since_latest_value)

# Index(['resource_state', 'name', 'distance', 'moving_time', 'elapsed_time',
#        'total_elevation_gain', 'type', 'sport_type', 'workout_type', 'id',
#        'start_date', 'start_date_local', 'timezone', 'utc_offset',
#        'location_city', 'location_state', 'location_country',
#        'achievement_count', 'kudos_count', 'comment_count', 'athlete_count',
#        'photo_count', 'trainer', 'commute', 'manual', 'private', 'visibility',
#        'flagged', 'gear_id', 'start_latlng', 'end_latlng', 'average_speed',
#        'max_speed', 'average_cadence', 'has_heartrate', 'average_heartrate',
#        'max_heartrate', 'heartrate_opt_out', 'display_hide_heartrate_option',
#        'elev_high', 'elev_low', 'upload_id', 'upload_id_str', 'external_id',
#        'from_accepted_tag', 'pr_count', 'total_photo_count', 'has_kudoed',
#        'athlete.id', 'athlete.resource_state', 'map.id',
#        'map.summary_polyline', 'map.resource_state'],
#       dtype='object')


# # Make a pie chart of total miles
# fig2, ax2 = plt.subplots(figsize=(8, 8))
# ax2.pie(df2.distance, autopct=autopct_format(df2.distance))
# ax2.legend(labels=df2.gear_id, loc='best', bbox_to_anchor=(.3, .3))
# ax2.set_title('Percentage of Total Miles')
# plt.savefig('imgs/total_distance_pie_chart.png', bbox_inches='tight', dpi=200)

# # Make a scatter plot comparing shoes by avg_pace (this is average pace of the SHOE not necessarily per run,
# # i.e., it is total distance / total time)
# fig3, ax3 = plt.subplots(figsize=(8, 8))
# ax3.scatter(df.distance, df.average_speed)
# ax3.set_title('Average Speed by Distance')
# # ax3.set_xticks(df.distance, df2.avg_pace_labels, rotation=90)
# ax3.set_xlabel('Distance')
# ax3.set_ylabel('Average Speed')
# ax3.invert_xaxis()
# ax3.xaxis.set_minor_locator(plticker.LinearLocator())
# fig3.tight_layout()
# plt.savefig('imgs/avg_pace_scatter_plot.png', bbox_inches='tight', dpi=200)

# # Make a box plot comparing shoes by relative effort
# fig4, ax4 = plt.subplots()
# ax4 = df.boxplot(by='gear_id', column=['suffer_score'], showmeans=True, meanline=True)
# plt.xticks(rotation=45)
# plt.minorticks_on()
# ax4.yaxis.set_minor_formatter(plticker.ScalarFormatter())
# ax4.get_figure().suptitle('')
# ax4.set_xlabel('Shoe')
# ax4.set_ylabel('Relative Effort')
# ax4.set_title('Relative Effort Box Plot')
# fig4.tight_layout()
# plt.savefig('imgs/relative_effort_box_plot', bbox_inches='tight', dpi=200)

# # Make a box plot comparing shoes by distance per activity.
# fig5, ax5 = plt.subplots()
# ax5 = df.boxplot(by='gear_id', column=['distance'], showmeans=True, meanline=True)
# plt.xticks(rotation=45)
# plt.minorticks_on()
# ax5.yaxis.set_minor_formatter(plticker.ScalarFormatter())
# ax5.get_figure().suptitle('')
# ax5.set_xlabel('Shoe')
# ax5.set_ylabel('Distance')
# ax5.set_title('Distance Box Plot')
# fig5.tight_layout()
# plt.savefig('imgs/distance_box_plot', bbox_inches='tight', dpi=200)

# # Make a boxplot comparing shoes by average cadence.
# fig6, ax6 = plt.subplots()
# ax6 = df.boxplot(by='gear_id', column=['avg_cadence'], showmeans=True, meanline=True)
# plt.xticks(rotation=45)
# plt.minorticks_on()
# ax6.yaxis.set_minor_formatter(plticker.ScalarFormatter())
# ax6.get_figure().suptitle('')
# ax6.set_xlabel('Shoe')
# ax6.set_ylabel('Cadence')
# ax6.set_title('Cadence Box Plot')
# fig6.tight_layout()
# plt.savefig('imgs/cadence_box_plot', bbox_inches='tight', dpi=200)

# # Make a box plot comparing shoes by heartrate during activity.
# fig7, ax7 = plt.subplots()
# ax7 = df.boxplot(by='gear_id', column=['average_heartrate'], showmeans=True, meanline=True)
# plt.xticks(rotation=45)
# plt.minorticks_on()
# ax7.yaxis.set_minor_formatter(plticker.ScalarFormatter())
# ax7.get_figure().suptitle('')
# ax7.set_xlabel('Shoe')
# ax7.set_ylabel('Heartrate')
# ax7.set_title('Heartrate Box Plot')
# fig7.tight_layout()
# plt.savefig('imgs/heartrate_box_plot', bbox_inches='tight', dpi=200)

# # Make a box plot comparing shoes by average speed during activity.
# fig8, ax8 = plt.subplots()
# ax8 = df.boxplot(by='gear_id', column=['average_speed'], showmeans=True, meanline=True)
# plt.xticks(rotation=45)
# plt.minorticks_on()
# ax8.yaxis.set_minor_formatter(plticker.ScalarFormatter())
# ax8.get_figure().suptitle('')
# ax8.set_xlabel('Shoe')
# ax8.set_ylabel('Speed')
# ax8.set_title('Speed Box Plot')
# fig8.tight_layout()
# plt.savefig('imgs/speed_box_plot', bbox_inches='tight', dpi=200)
