
def LISTEN_BRANCH      = 'feature/test-pipeline'                   // only build when webhook branch == this
def WEBHOOK_TOKEN_ID   = 'nextmailer-generic-webhook-token-id'     // Secret Text credential ID
def ENV_FILE_CREDENTIAL = 'nextmailer-test-env-file-id'                  // ID of the file credential for .env
def DOMAIN = 'nextmailer.logicmatrix.us'                                // Domain name to use
def TEAMS_WEBHOOK_CREDID = 'teams-webhook-url-credential-id'  // Jenkins Secret Text credential ID for Teams webhook URL

def sendTeamsNotification = { String status, String job, String build, String link, String webhookUrl ->
    def payload = [
        'title'     : 'Jenkins Pipeline Notification',
        'status'    : status,
        'job'       : job,
        'build'     : build,
        'link'      : link,

    ]

    httpRequest(
        httpMode: 'POST',
        contentType: 'APPLICATION_JSON',
        requestBody: groovy.json.JsonOutput.toJson(payload),
        url: webhookUrl
    )
}
pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }
  environment {
    DOMAIN = "${DOMAIN}"
    TEAMS_WEBHOOK_URL = credentials("${TEAMS_WEBHOOK_CREDID}")
  }
  triggers {
    // Generic Webhook Trigger (requires Generic Webhook Trigger plugin)
    GenericTrigger(
      tokenCredentialId: WEBHOOK_TOKEN_ID,
      // Pull useful bits from common GitHub push payload
      genericVariables: [
        // full ref like "refs/heads/dev"
        [key: 'GH_REF',   value: '$.ref'],
        // actor display name
        [key: 'ACTOR',    value: '$.sender.login'],
        // repository name
        [key: 'REPO',     value: '$.repository.full_name']
      ],
      //  only accept the branch you want
      regexpFilterText: '$GH_REF',
      regexpFilterExpression: '^refs/heads/' + java.util.regex.Pattern.quote(LISTEN_BRANCH) + '$',
      // quiet logs
      printContributedVariables: false,
      printPostContent: false,
      // Optional nicety
      causeString: 'Generic webhook by $ACTOR on $REPO ($GH_REF)',
    )
  }

  stages {
    stage('Notify Start') {
        steps {
            script {
              def message = "🚀 Pipeline STARTED"
              sendTeamsNotification(message, env.JOB_NAME, env.BUILD_NUMBER, env.BUILD_URL, env.TEAMS_WEBHOOK_URL)
            }
        }
    }

    stage('Checkout') {
      steps {
        echo 'Checking out the repository...'
        checkout scm
      }
    }

    stage('Load .env Securely') {
      steps {
        script {
          withCredentials([file(credentialsId: ENV_FILE_CREDENTIAL, variable: 'ENV_FILE')]) {
            // Copy .env securely into workspace
            sh 'cp "$ENV_FILE" .env && chmod 600 .env'
          }
        }
      }
    }
    stage('Build') {
      steps {
        dir("${env.REPO_NAME}") {
          echo 'Building image...'
          sh 'docker compose build'
        }
      }
    }
    stage('DB Migrate & Upgrade') {
      steps {
        script {
            sh '''
              docker compose run --rm web flask db migrate
              docker compose run --rm web flask db upgrade
            '''
        }
      }
    }
    stage('Run') {
      steps {
        echo 'Running containers...'
        sh 'docker compose up -d'
      }
    }
  }

  post {
    always {
      script {
            echo 'Cleaning up...'

            // Delete sensitive .env file explicitly
            sh 'rm -f .env || true'
            // Delete subfolder if defined
            deleteDir()
      }
    }
    success {
      echo 'Deployed successfully.'
        script {
            echo 'Deployed successfully.'
            def message = "✅ SUCCESS"
            sendTeamsNotification(message, env.JOB_NAME, env.BUILD_NUMBER, env.BUILD_URL, env.TEAMS_WEBHOOK_URL)
        }
    }
    failure {
      script {
            echo 'Build failed.'
            def message = "❌ FAILED"
            sendTeamsNotification(message, env.JOB_NAME, env.BUILD_NUMBER, env.BUILD_URL, env.TEAMS_WEBHOOK_URL)
      }
    }
  }
}
