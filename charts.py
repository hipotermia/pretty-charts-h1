from flask import Flask
import dateutil.parser
from datetime import timezone
import requests
import webbrowser

app = Flask(__name__)

@app.route('/')
def hipotermia():
	try:
		r = requests.get('https://hackerone.com/current_user', cookies={'__Host-session': cookie})
		csrf = r.json()['csrf_token']
		profile_pic = r.json()['profile_picture_urls']['medium']

		r = requests.post('https://hackerone.com/bugs.json?limit=1000', cookies={'__Host-session': cookie}, headers={'x-csrf-token': csrf})
		bugs = r.json()['bugs']
	except:
		return 'Invalid cookie'

	days = [0] * 7
	hours = [0] * 24
	for bug in bugs:
		d = dateutil.parser.parse(bug['created_at']).replace(tzinfo=timezone.utc).astimezone(tz=None)
		hours[d.hour] += 1
		days[d.weekday()] += 1

	return '''
    <html><head><title>Pretty charts for h1</title></head><body>
<script src="https://code.highcharts.com/highcharts.js"></script>

<figure class="highcharts-figure">
    <div id="container"></div>
    <div id="container2"></div>
</figure>
<img style="display:block;margin:auto" src="''' + profile_pic + '''">
<script>
Highcharts.chart('container', {
    title: {
        text: 'Submissions by Hour'
    },
    legend: {
    	enabled: false
    },
    xAxis: {
        labels: {format: '{value}:00'}
    },
    yAxis: {
        title: {text: null}
    },
    series: [{
        name: 'Submissions',
        data: ''' + str(hours) + '''
    }]
});
Highcharts.chart('container2', {
    title: {
        text: 'Submissions by Weekday'
    },
    chart: {
        type: 'column'
    },
    xAxis: {
        categories: ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    },    
    yAxis: {
        title: {text: null}
    },
    legend: {
    	enabled: false
    },
    series: [{
        name: 'Submissions',
        data: ''' + str(days) + '''
    }]
});
</script>

</body></html>
    '''

if __name__ == '__main__':
	global cookie
	cookie = input('Enter your HackerOne cookie (__Host-session): ').strip()
	if cookie:
		webbrowser.open('http://localhost:5000')
		app.run()
