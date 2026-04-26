"""
Script to populate the OctoFit Tracker database with test data.
Run with: python populate_db.py
"""

import os
import django
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'octofit_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from fitness.models import UserProfile, Team, Activity, Achievement, LeaderboardEntry

def clear_database():
    """Clear existing data"""
    print("Clearing existing data...")
    # Just clear the fitness models (djongo has issues with NOT queries)
    try:
        Team.objects.all().delete()
        Activity.objects.all().delete()
        Achievement.objects.all().delete()
        LeaderboardEntry.objects.all().delete()
        UserProfile.objects.all().delete()
    except Exception as e:
        print(f"Note: Could not clear all data, proceeding anyway: {e}")
    print("Ready to populate.")

def create_test_users():
    """Create test users"""
    print("Creating test users...")
    users_data = [
        {'username': 'paul_octo', 'email': 'paul@mergington.edu', 'first_name': 'Paul', 'last_name': 'Octo'},
        {'username': 'jessica_cat', 'email': 'jessica@mergington.edu', 'first_name': 'Jessica', 'last_name': 'Cat'},
        {'username': 'alex_runner', 'email': 'alex@mergington.edu', 'first_name': 'Alex', 'last_name': 'Runner'},
        {'username': 'emma_strong', 'email': 'emma@mergington.edu', 'first_name': 'Emma', 'last_name': 'Strong'},
        {'username': 'mike_swimmer', 'email': 'mike@mergington.edu', 'first_name': 'Mike', 'last_name': 'Swimmer'},
    ]
    
    users = []
    for user_data in users_data:
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password='testpassword123'
            )
            UserProfile.objects.create(
                user=user,
                bio=f"Fitness enthusiast - {user_data['first_name']}",
                total_points=0
            )
            users.append(user)
            print(f"  Created user: {user.username}")
        except Exception as e:
            print(f"  Error creating {user_data['username']}: {e}")
            # Try to retrieve existing user
            try:
                user = User.objects.get(username=user_data['username'])
                users.append(user)
                print(f"  Using existing user: {user.username}")
            except User.DoesNotExist:
                print(f"  Skipping {user_data['username']}")
    
    return users

def create_teams(users):
    """Create test teams"""
    print("Creating teams...")
    teams_data = [
        {'name': 'Team Warriors', 'description': 'The strongest team in school', 'leader': users[0], 'members': [users[0], users[2]]},
        {'name': 'Team Lightning', 'description': 'Speed and agility champions', 'leader': users[1], 'members': [users[1], users[3]]},
        {'name': 'Team Aqua', 'description': 'Water sports enthusiasts', 'leader': users[4], 'members': [users[4]]},
    ]
    
    teams = []
    for team_data in teams_data:
        member_ids = [user.id for user in team_data['members']]
        team = Team.objects.create(
            name=team_data['name'],
            description=team_data['description'],
            leader=team_data['leader'],
            member_ids=member_ids
        )
        teams.append(team)
        print(f"  Created team: {team.name}")
    
    return teams

def create_activities(users):
    """Create test activities"""
    print("Creating activities...")
    activity_count = 0
    
    for user in users:
        activities_data = [
            {'type': 'running', 'duration': 30, 'distance': 5.0, 'calories': 300, 'points': 100},
            {'type': 'walking', 'duration': 45, 'distance': 3.5, 'calories': 150, 'points': 50},
            {'type': 'strength', 'duration': 60, 'distance': None, 'calories': 400, 'points': 120},
            {'type': 'cycling', 'duration': 45, 'distance': 15.0, 'calories': 350, 'points': 110},
        ]
        
        for idx, activity_data in enumerate(activities_data):
            date = timezone.now() - timedelta(days=idx)
            activity = Activity.objects.create(
                user=user,
                activity_type=activity_data['type'],
                duration_minutes=activity_data['duration'],
                distance_km=activity_data['distance'],
                calories_burned=activity_data['calories'],
                points_earned=activity_data['points'],
                date=date,
                description=f"Great {activity_data['type']} workout!"
            )
            activity_count += 1
            print(f"  Created activity: {user.username} - {activity_data['type']}")
    
    print(f"Total activities created: {activity_count}")

def create_achievements():
    """Create test achievements"""
    print("Creating achievements...")
    achievements_data = [
        {
            'name': 'First Step',
            'description': 'Complete your first activity',
            'icon': 'https://via.placeholder.com/64?text=First+Step',
            'requirement_points': 0,
        },
        {
            'name': 'Century Runner',
            'description': 'Earn 100 points in running activities',
            'icon': 'https://via.placeholder.com/64?text=Century',
            'requirement_points': 100,
        },
        {
            'name': 'Fitness Pioneer',
            'description': 'Log 500 total activity points',
            'icon': 'https://via.placeholder.com/64?text=Pioneer',
            'requirement_points': 500,
        },
    ]
    
    for achievement_data in achievements_data:
        achievement = Achievement.objects.create(
            name=achievement_data['name'],
            description=achievement_data['description'],
            icon=achievement_data['icon'],
            requirement_points=achievement_data['requirement_points'],
            users_earned_ids=[]
        )
        print(f"  Created achievement: {achievement.name}")

def create_leaderboard(users):
    """Create leaderboard entries"""
    print("Creating leaderboard entries...")
    rankings = sorted(
        [(user, Activity.objects.filter(user=user).aggregate(total=Sum('points_earned'))['total'] or 0) 
         for user in users],
        key=lambda x: x[1],
        reverse=True
    )
    
    for rank, (user, total_points) in enumerate(rankings, 1):
        LeaderboardEntry.objects.create(
            user=user,
            rank=rank,
            total_points=total_points
        )
        print(f"  {rank}. {user.username} - {total_points} points")

def populate_database():
    """Main function to populate database"""
    print("\n" + "="*50)
    print("Starting OctoFit Tracker Database Population")
    print("="*50 + "\n")
    
    try:
        clear_database()
        users = create_test_users()
        teams = create_teams(users)
        create_activities(users)
        create_achievements()
        create_leaderboard(users)
        
        print("\n" + "="*50)
        print("Database population completed successfully!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"Error during population: {e}")
        raise

if __name__ == '__main__':
    populate_database()
