
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'flowpilot'
        IMAGE_TAG = '1.0.0'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'FlowPilot source code checked out from GitHub'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    rm -rf .venv
                    python3 --version
                    python3 -m venv .venv
                    .venv/bin/python --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/python -m pip install -r requirements.txt
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

        stage('Build Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        docker build \
                            -t "$DOCKERHUB_USERNAME/$IMAGE_NAME:$IMAGE_TAG" .
                    '''
                }
            }
        }

        stage('Verify Docker Hub Credentials') {
    steps {
        withCredentials([usernamePassword(
            credentialsId: 'dockerhub-credentials',
            usernameVariable: 'DOCKERHUB_USERNAME',
            passwordVariable: 'DOCKERHUB_TOKEN'
        )]) {
            sh '''
                set +x

                echo "Docker Hub username: $DOCKERHUB_USERNAME"

                if [ -n "$DOCKERHUB_TOKEN" ]; then
                    echo "Docker Hub token: Available"
                else
                    echo "Docker Hub token: Missing"
                    exit 1
                fi

                echo "$DOCKERHUB_TOKEN" | docker login \
                    --username "$DOCKERHUB_USERNAME" \
                    --password-stdin
            '''
        }
    }
}

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        set +x

                        echo "$DOCKERHUB_TOKEN" | docker login \
                            --username "$DOCKERHUB_USERNAME" \
                            --password-stdin

                        docker push \
                            "$DOCKERHUB_USERNAME/$IMAGE_NAME:$IMAGE_TAG"

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'FlowPilot CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'FlowPilot CI/CD pipeline failed. Check the console output.'
        }

        always {
            echo 'FlowPilot pipeline execution finished.'
        }
    }
}
