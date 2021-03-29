from flask import Flask, jsonify
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
<button style="display:block;margin:auto" onclick="location.href='/bounty-detail'" type="button">Go to Bounty detail</button>
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


@app.route('/bounty-detail')
def bounty_detail():
	try:
		r = requests.get('https://hackerone.com/current_user', cookies={'__Host-session': cookie})
		profile_pic = r.json()['profile_picture_urls']['medium']
	except:
		return 'Invalid cookie'

	return '''
<html><head><title>Pretty charts for h1</title></head><body>
<script src="https://code.highcharts.com/highcharts.js"></script>

<style>
.lds-dual-ring {
  display: inline-block;
  width: 80px;
  height: 80px;
}
.lds-dual-ring:after {
  content: " ";
  display: block;
  width: 64px;
  height: 64px;
  margin: 8px;
  border-radius: 50%;
  border: 6px solid #fcf;
  border-color: #fcf transparent #fcf transparent;
  animation: lds-dual-ring 1.2s linear infinite;
}
@keyframes lds-dual-ring {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>

<div style="text-align: center;" id="loading">
    <div class="lds-dual-ring"></div>
    <p>Loading... (super slow - status on terminal)
</div>

<div style="text-align: center;">
    <figure class="highcharts-figure" style="display:inline-block">
        <div id="container2"></div>
    </figure>
    <figure class="highcharts-figure" style="display:inline-block">
        <div id="container"></div>
    </figure>
</div>
<img style="display:block;margin:auto" src="''' + profile_pic + '''">

<script>
    function draw(bounties, severities){
        document.getElementById('loading').hidden = true;

        Highcharts.chart('container', {
            chart: {
                type: 'pie'
            },
            title: {
                text: 'Percetage of income by severity'
            },
            tooltip: {
                pointFormat: '{series.name}: <b>$ {point.y}</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                    }
                }
            },
            series: [{
                name: 'Bounties',
                data: bounties
            }]
        });
        Highcharts.chart('container2', {
            chart: {
                type: 'pie'
            },
            title: {
                text: 'Number of bounties by severity'
            },
            plotOptions: {
                pie: {
                    dataLabels: {
                        enabled: true,
                        distance: -50,
                        style: {
                            fontWeight: 'bold',
                            color: 'white'
                        }
                    },
                    startAngle: -90,
                    endAngle: 90,
                    center: ['50%', '75%'],
                    size: '110%',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.y}'
                    }
                }
            },
            series: [{
                name: 'Bounties',
                data: severities
            }]
        });
    }

    fetch('/bounty-detail-data')
    .then(function(response) {return response.json()})
    .then(function(data) {
        var bounties = [];
        var severities = [];
        for (key in data){
            bounties.push({name: key, y: data[key].bounties});
            severities.push({name: key, y: data[key].n});
        }
        draw(bounties, severities);
    });
</script>
</body></html>
'''

@app.route('/bounty-detail-data')
def bounty_detail_data():
	try:
		r = requests.get('https://hackerone.com/current_user', cookies={'__Host-session': cookie})
		csrf = r.json()['csrf_token']
		username = r.json()['username']

		r = requests.post('https://hackerone.com/bugs.json?limit=1000', cookies={'__Host-session': cookie}, headers={'x-csrf-token': csrf})
		bugs = r.json()['bugs']
	except:
		return 'Invalid cookie'
	
	severities = {}
	for i, bug in enumerate(bugs):
		count = False
		id = bug['id']
		severity = bug['severity_rating']

		detail = requests.get('https://hackerone.com/reports/' + str(id) + '.json', cookies={'__Host-session': cookie}).json()

		for activity in detail['activities']:
			if activity['type'] == 'Activities::BountyAwarded' and activity['collaborator']['username'] == username:
				if severity not in severities:
					severities[severity] = {'n': 0, 'bounties': 0}
				severities[severity]['bounties'] += float(activity['bounty_amount']) + float(activity['bonus_amount'])
				count = True
		if count:
			severities[severity]['n'] += 1

		print('[' + str(i) + '/' + str(len(bugs)) + ']', severities)
	return jsonify(severities)

if __name__ == '__main__':
	global cookie
	cookie = input('Enter your HackerOne cookie (__Host-session): ').strip()
	if cookie:
		webbrowser.open('http://localhost:5000')
		app.run()
