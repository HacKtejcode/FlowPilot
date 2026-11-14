
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'FlowPilot source code checked out from GitHub'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 --version
                    python3 -m venv .venv
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    .venv/bin/python -m pytest -v
                '''
            }
        }
    }

    post {
        success {
            echo 'FlowPilot CI Pipeline completed successfully!'
        }
        failure {
            echo 'FlowPilot CI Pipeline failed. Check the console output.'
        }
    }
}
