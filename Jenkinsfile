properties([
    parameters([
        string(defaultValue: '', description: 'The version from PyPI to build', name: 'BUILD_VERSION')
    ]),
    pipelineTriggers([])
])

def configs = [
    [
        label: 'windows',
        versions: ['py26', 'py27', 'py33', 'py34', 'py35', 'py36'] 
    ]
]
def build(version, label) {
    //echo 'version - ' + version
    //echo 'label - ' + label
    def repo_name = 'github_publish'               //can be extracted from url.git
    def repo_owner = 'umihai1'                       //can be extracted from url.git
    def project_name = 'github_publish'                  //can be extracted from the project

    try {
        timeout(time: 30, unit: 'MINUTES') {
            if (label.contains("windows")) {
                def pythonPath = [
                    py26: "C:\\Python26\\python.exe",
                    py27: "C:\\Python27\\python.exe",
                    py33: "C:\\Python33\\python.exe",
                    py34: "C:\\Python34\\python.exe",
                    py35: "C:\\Python35\\python.exe",
                    py36: "C:\\Python36\\python.exe"
                ]
                
                echo 'Check out scm...'
                dir (repo_name){
                    checkout scm
                }
                
                echo 'Install Python Virtual Environment - ' + version + ' - ' + label
                bat """
                    rem wmic qfe
                    @set PATH="C:\\Python35";"C:\\Python35\\Scripts";%PATH%
                    @set PYTHON="${pythonPath[version]}"
                    python --version
                    python -m venv -p %PYTHON% .release_${version}
                    call .release_${version}\\Scripts\\activate
                    python --version
                    cd ${repo_name}
                    pip install -r requirements_develop.txt
                    python -m coverage run test/run_all.py
                    python -m coverage xml -i || exit 0
                    python -m pylint --rcfile .pylintrc -f parseable github_publish > pylint.report || exit 0
                    """
                
                echo 'Reporting'
                echo '...CoberturaPublisher...'
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

                echo '...junit report...'
                junit repo_name + '/test-reports/*.xml'

                echo '...WarningsPublisher...'
                step([$class: 'WarningsPublisher',
                    parserConfigurations: [[parserName: 'PYLint', pattern: repo_name + '/pylint.report']],
                    unstableTotalAll: '5000',
                    usePreviousBuildAsReference: true])
            } // end label.contains("windows")
            //archiveArtifacts artifacts: "wheelhouse/cryptography*.whl"
        } // end timeout(time: 30, unit: 'MINUTES')
    } // end timeout
    catch(err) {
        currentBuild.result = 'FAILURE'
        //echo 'err' + err
        throw err
    } 
    finally {
        echo 'Clean workspace...'
       cleanWs deleteDirs: true
    }
}

def builders = [:]
for (config in configs) {
    def label = config["label"]
    def versions = config["versions"]
    for (_version in versions) {
        def version = _version
        if (label.contains("windows")) {
            def combinedName = "${label}-${version}"
            builders[combinedName] = {
                node(label) {
                    ws("jobs/${env.JOB_NAME}/ws"){
                        stage(combinedName) {
                            build(version, label)
                        }
                    }
                }
            }
        }
    }
}

parallel builders