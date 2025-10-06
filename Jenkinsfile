pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }
  stages {
    stage('Checkout') {
          steps {
            echo 'Checking out the repository...'
            checkout scm
          }
    }



  }

  post {
    always {
      echo "🧹 Cleaning up ${env.REPO_NAME}..."
      dir("${env.REPO_NAME}") {
        deleteDir()
      }
        }
    success {
      echo '✅ App deployed successfully.'
        }
    failure {
      echo '❌ Build failed.'
        }
    }
}