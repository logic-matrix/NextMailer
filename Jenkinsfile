
def LISTEN_BRANCH      = 'feature/test-pipeline'                   // only build when webhook branch == this
def WEBHOOK_TOKEN_ID   = 'nextmailer-generic-webhook-token-id' // Secret Text credential ID
pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
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
      regexpFilterText: '$REF',
      regexpFilterExpression: '^refs/heads/' + java.util.regex.Pattern.quote(LISTEN_BRANCH) + '$',
      // quiet logs
      printContributedVariables: false,
      printPostContent: false,
      // Optional nicety
      causeString: 'Generic webhook by $ACTOR on $REPO ($GH_REF)',
    )
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