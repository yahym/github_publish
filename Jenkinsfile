node(){
    def python_home = "c:/python-3.5.3"
    def repo_name = 'github_publish'               //can be extracted from url.git
    def repo_owner = 'umihai1'                       //can be extracted from url.git
    def project_name = 'github_publish'                  //can be extracted from the project
    def version = '1.0.0'                           //can be extracted from __init__.py maybe_' + env.currentBuid.Number

    // Try to keep the workspace path as short as possible, other wise you will
    // get in trouble with python package installation :)
    // - this is the reason for replacing 'workspace' with 'ws'
    ws("jobs/${env.JOB_NAME}/ws") {
        try{
        stage("Checkout SCM - ${env.JOB_NAME}"){
            echo 'Already done by Jenkinsfile, but need it again here for now...'
            dir (repo_name){
                checkout scm
            }
        }

        stage("Install Python Virtual Environment") {
            createVirtualEnv 'pyvenv'
        }


        stage('Preparing PythonEnv 3.5.3'){
            withCredentials([usernamePassword(credentialsId: '99176a2e-9012-4b19-95f7-926d65985d05', passwordVariable: 'password', usernameVariable: 'user')]) {
                executeIn 'pyvenv', 'python --version'
                executeIn 'pyvenv', 'pip3 install -r ' + repo_name + '/requirements_develop.txt'
            }
        }

        stage('Running tests'){
            executeIn 'pyvenv', 'python --version'
            executeIn 'pyvenv', 'cd ' + repo_name + ' && python -m coverage run test/run_all.py'
            executeIn 'pyvenv', 'cd ' + repo_name + ' && python -m coverage xml -i || exit 0'
            executeIn 'pyvenv', 'cd ' + repo_name + ' && python -m pylint --rcfile .pylintrc -f parseable -d I0011,R0801 github_publish > pylint.report || exit 0'
            //executeIn 'pyvenv', 'cd ' + repo_name + ' && python -m nose -v --with-xunit --with-coverage --cover-package=github_publish || exit 0'

        }

        stage ('Reporting'){
            echo 'CoberturaPublisher...'
            step([$class: 'CoberturaPublisher',
                autoUpdateHealth: false,
                autoUpdateStability: false,
                coberturaReportFile: repo_name + '/coverage.xml',
                failNoReports: false,
                failUnhealthy: false,
                failUnstable: false,
                maxNumberOfBuilds: 0,
                onlyStable: false,
                sourceEncoding: 'ASCII',
                zoomCoverageChart: false])

            echo 'junit report...'
            junit repo_name + '/test-reports/*.xml'

            echo 'WarningsPublisher...'
            step([$class: 'WarningsPublisher',
                parserConfigurations: [[parserName: 'PYLint', pattern: repo_name + '/pylint.report']],
                unstableTotalAll: '5000',
                usePreviousBuildAsReference: true])
        }

        stage('Generating application *.exe'){
            echo 'Generating the application...'
            def pyinstaller = 'pyvenv/scripts/pyinstaller.exe'
            executeIn 'pyvenv', 'cd ' + repo_name + ' && ' + pyinstaller + ' github_publish.spec'
        }

        stage ('Publish to GitHub Releases and internal PyPi'){
            echo 'Build artifacts based on dist'
            archiveArtifacts allowEmptyArchive: true, artifacts: repo_name + '/dist/*'
            //if ${owner} == 'umihai1' && ${env.JOB_NAME} == 'master' {
                echo 'Upload to internal PyPi'
                bat """
                    rem `.pypirc` should be copied in `%USERPROFILE%` to be able to upload to pypi-server
                    echo %USERPROFILE%
                """
                executeIn 'pyvenv', 'cd ' + repo_name + ' && python setup.py sdist upload'

                echo 'Upload to GitHub Releases'
                withCredentials([usernamePassword(credentialsId: '99176a2e-9012-4b19-95f7-926d65985d05', passwordVariable: 'password', usernameVariable: 'user')]) {
                    bat """
                    """
                //}
            }

            //TODO: Delete dist/* folder, but add a link into Jenkins to GitHub release and pypi
        }

        stage('Merge Pull Request'){
            echo 'GhprbPullRequestMerge - Not done yet...'
            //withCredentials([usernamePassword(credentialsId: '99176a2e-9012-4b19-95f7-926d65985d05', passwordVariable: 'password', usernameVariable: 'user')]) {
                //step([$class: 'GhprbPullRequestMerge',
                    //allowMergeWithoutTriggerPhrase: true,
                    //deleteOnMerge: false,
                    //disallowOwnCode: false,
                    //failOnNonMerge: false,
                    //mergeComment: '',
                    //onlyAdminsMerge: false])
            //}
        }
        }
        catch(err) {
            currentBuild.result = 'FAILURE'
            throw err
        } finally {
            stage("Cleaning workspace"){
               echo 'Clean workspace...'
               cleanWs deleteDirs: true
            }
        }
    }
}

// one of the workaround
def createVirtualEnv(String name) {
    bat """
        py -3 -m venv ${name}
    """
}

def executeIn(String environment, String script) {
    def ws_path = pwd()
    def env_local = environment
    bat """
        "${ws_path}/${env_local}/Scripts/activate.bat" && ${script}
    """
}

