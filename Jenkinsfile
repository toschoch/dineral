pipeline {
    agent {
        docker { image 'python:3-alpine' }
    }
    stages {
        stage('Test') {
            steps {
                echo "Testing..."
            }
        }
        stage('Build') {
            steps {
                echo "Building..."
                sh 'uname'
            }
        }
    }
}