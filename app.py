from flask import Flask, render_template, request, redirect, url_for
import boto3
import uuid

app = Flask(__name__)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('research_profiles')

def get_match_score(interests_a, interests_b):
    """Simple keyword matching - split by comma, count overlaps."""
    set_a = set(w.strip().lower() for w in interests_a.split(','))
    set_b = set(w.strip().lower() for w in interests_b.split(','))
    overlap = set_a & set_b
    total = set_a | set_b
    if not total:
        return 0, []
    score = int(len(overlap) / len(total) * 100)
    return score, list(overlap)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/professor', methods=['GET', 'POST'])
def professor():
    if request.method == 'POST':
        table.put_item(Item={
            'id': str(uuid.uuid4()),
            'type': 'professor',
            'name': request.form['name'],
            'department': request.form['department'],
            'interests': request.form['interests'],
            'lab': request.form.get('lab', '')
        })
        return redirect(url_for('home'))
    return render_template('professor_form.html')

@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        student_interests = request.form['interests']

        # Get all professors from DynamoDB
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('type').eq('professor')
        )
        professors = response['Items']

        # Score each professor
        matches = []
        for prof in professors:
            score, shared = get_match_score(student_interests, prof.get('interests', ''))
            if score > 0:
                matches.append({
                    'name': prof['name'],
                    'department': prof['department'],
                    'interests': prof['interests'],
                    'lab': prof.get('lab', 'N/A'),
                    'score': score,
                    'shared': shared
                })

        matches.sort(key=lambda x: x['score'], reverse=True)

        # Save student profile
        table.put_item(Item={
            'id': str(uuid.uuid4()),
            'type': 'student',
            'name': request.form['name'],
            'program': request.form['program'],
            'interests': student_interests
        })

        return render_template('results.html',
            matches=matches,
            student_name=request.form['name'],
            student_interests=student_interests
        )
    return render_template('student_form.html')

if __name__ == '__main__':
    app.run(debug=True)
