import argparse as ap
from pprint import pprint
__version__ = r'0.0.1'

HELP = """
Global options:
        -h, --help           Show this help
        -v, --verbose        Be verbose
        -q, --quiet          Do not print anything, even errors (except if --verbose is specified)
            --version        Print version

Verbs:
    delete:
        -s, --security-token Github token (required if $GITHUB_TOKEN not set)
        -u, --user           Github repo user or organisation (required if $GITHUB_USER not set)
        -r, --repo           Github repo (required if $GITHUB_REPO not set)
        -t, --tag            Git tag of release to delete (*)
    download:
        -s, --security-token Github token ($GITHUB_TOKEN if set). required if repo is private.
        -u, --user           Github repo user or organisation (required if $GITHUB_USER not set)
        -r, --repo           Github repo (required if $GITHUB_REPO not set)
        -l, --latest         Download latest release (required if tag is not specified)
        -t, --tag            Git tag to download from (required if latest is not specified) (*)
        -n, --name           Name of the file (*)
    edit:
        -s, --security-token Github token (required if $GITHUB_TOKEN not set)
        -u, --user           Github repo user or organisation (required if $GITHUB_USER not set)
        -r, --repo           Github repo (required if $GITHUB_REPO not set)
        -t, --tag            Git tag to edit the release of (*)
        -n, --name           New name of the release (defaults to tag)
        -d, --description    New release description, use - for reading a description from stdin (de
faults to tag)
            --draft          The release is a draft
        -p, --pre-release    The release is a pre-release
    info:
        -s, --security-token Github token ($GITHUB_TOKEN if set). required if repo is private.
        -u, --user           Github repo user or organisation (required if $GITHUB_USER not set)
        -r, --repo           Github repo (required if $GITHUB_REPO not set)
        -t, --tag            Git tag to query (optional)
        -j, --json           Emit info as JSON instead of text
    release:
        -s, --security-token Github token (required if $GITHUB_TOKEN not set)
        -u, --user           Github repo user or organisation (required if $GITHUB_USER not set)
        -r, --repo           Github repo (required if $GITHUB_REPO not set)
        -t, --tag            Git tag to create a release from (*)
        -n, --name           Name of the release (defaults to tag)
        -d, --description    Release description, use - for reading a description from stdin (defaul
ts to tag)
        -c, --target         Commit SHA or branch to create release of (defaults to the repository d
efault branch)
            --draft          The release is a draft
        -p, --pre-release    The release is a pre-release
    upload:
        -s, --security-token Github token (required if $GITHUB_TOKEN not set)
        -u, --user           Github repo user or organisation (required if $GITHUB_USER not set)
        -r, --repo           Github repo (required if $GITHUB_REPO not set)
        -t, --tag            Git tag to upload to (*)
        -n, --name           Name of the file (*)
        -l, --label          Label (description) of the file
        -f, --file           File to upload (use - for stdin) (*)
        -R, --replace        Replace asset with same name if it already exists (WARNING: not atomic,
 failure to upload will remove the original asset too)
"""

class ArgHolder:
    """Hold the arguments and keyword arguments to 
       later unpack into a function call"""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
class ArgHandler():
    def __init__(self,
                prog="github_publish",
                version="0.0.1",
                parser=ap.ArgumentParser):
        self.help = HELP
        self.security_token = ArgHolder('-s', '--security-token', dest='security_token', help='Github token (required if $GITHUB_TOKEN not set)')
        self.owner = ArgHolder('-o', '--owner', dest='owner', required = False, help='Github repo owner or organisation (required if $GITHUB_USER not set)')
        self.user = ArgHolder('-u', '--user', dest='user', help='Github repo user or organisation (required if $GITHUB_USER not set)')
        self.password = ArgHolder('-p', '--password', dest='password',  required = False, help='Github user password (required if $GITHUB_PASSWORD not set)')
        self.repo = ArgHolder('-r', '--repo', dest='repo', help='Github repo (required if $GITHUB_REPO not set')
        self.tag = ArgHolder('-t', '--tag', dest='tag', help='Git tag of release to delete (*)')
        self.name = ArgHolder('-n', '--name', dest='name', help='Name of the file (*)')
        self.latest = ArgHolder('-l', '--latest', dest='latest', help='Download latest release (required if tag is not specified')
        self.description = ArgHolder('-d', '--description', dest='description', help='New release description, use - for reading a description from stdin (defaults to tag')
        self.draft = ArgHolder('--draft', dest='draft', help='The release is a draft')
        self.pre_release = ArgHolder('--pre-release', dest='pre_release', help='The release is a pre-release')
        self.json = ArgHolder('-j', '--json', dest='json', required = False, help='Emit info as JSON instead of text')
        self.target = ArgHolder('-c', '--target', dest='target', help='Commit SHA or branch to create release of (defaults to the repository default branch')
        self.label = ArgHolder('-l', '--label', dest='label', help='Label (description) of the file')
        self.file = ArgHolder('-f', '--file', dest='file', help='File to upload (use - for stdin) (*)')
        self.replace = ArgHolder('-R', '--replace', dest='replace', required = False, help='Replace asset with same name if it already exists (WARNING: not atomic, failure to upload will remove the original asset too')
        self.latest = ArgHolder('--latest', dest='latest', action='store_true', required = False, help='Latest release  (use - for stdin) (*)')
        self.assets = ArgHolder('--assets', dest='assets', action='store_true', required = False, help='Assets for release  (use - for stdin) (*)')
        self.download_all = ArgHolder('--download_all', dest='download_all', action='store_true', required = False, help='Download all assets for release  (use - for stdin) (*)')
        
        # Init parser
        self.parser = parser(prog=prog)
        
        # Global optional arguments
        self.proxy = self.parser.add_argument('--proxy', help='Add the internet proxy, e.g. "http://user:password@server.com:8080"')
        self.version = self.parser.add_argument('--version', action='version', version="%(prog)s ("+__version__+")", help='Get program version')
        
         # add a mandatory subcommand available after parsing at args.subcommand
        self.subparsers = self.parser.add_subparsers(dest='subcommand')
        self.subparsers.required = True
        
        #Verbs:
            #delete:
        self.delete = self.subparsers.add_parser('delete', help='Delete a release or a tag')
        self.delete.add_argument(*self.security_token.args, **self.security_token.kwargs)
        self.delete.add_argument(*self.owner.args, **self.owner.kwargs)
        self.delete.add_argument(*self.user.args, **self.user.kwargs)
        self.delete.add_argument(*self.password.args, **self.password.kwargs)
        self.delete.add_argument(*self.repo.args, **self.repo.kwargs)
        self.delete.add_argument(*self.tag.args, **self.tag.kwargs)
            
            #download:
        self.download = self.subparsers.add_parser('download', help='Download a release or a tag')
        self.download.add_argument(*self.security_token.args, **self.security_token.kwargs)
        self.download.add_argument(*self.owner.args, **self.owner.kwargs)
        self.download.add_argument(*self.user.args, **self.user.kwargs)
        self.download.add_argument(*self.password.args, **self.password.kwargs)
        self.download.add_argument(*self.repo.args, **self.repo.kwargs)
        self.download.add_argument(*self.tag.args, **self.tag.kwargs)
        self.download.add_argument(*self.name.args, **self.name.kwargs)
        self.download.add_argument(*self.latest.args, **self.latest.kwargs)
        self.download.add_argument(*self.download_all.args, **self.download_all.kwargs)
            
            #edit:
        self.edit = self.subparsers.add_parser('edit', help='Edit a release or a tag')
        self.edit.add_argument(*self.security_token.args, **self.security_token.kwargs)
        self.edit.add_argument(*self.owner.args, **self.owner.kwargs)
        self.edit.add_argument(*self.user.args, **self.user.kwargs)
        self.edit.add_argument(*self.password.args, **self.password.kwargs)
        self.edit.add_argument(*self.repo.args, **self.repo.kwargs)
        self.edit.add_argument(*self.tag.args, **self.tag.kwargs)
        self.edit.add_argument(*self.name.args, **self.name.kwargs)
        self.edit.add_argument(*self.description.args, **self.description.kwargs)
        self.edit.add_argument(*self.draft.args, **self.draft.kwargs)
        self.edit.add_argument(*self.pre_release.args, **self.pre_release.kwargs)
            
            #info:
        self.info = self.subparsers.add_parser('info', help='Info a release or a tag')
        self.info.add_argument(*self.security_token.args, **self.security_token.kwargs)
        self.info.add_argument(*self.owner.args, **self.owner.kwargs)
        self.info.add_argument(*self.user.args, **self.user.kwargs)
        self.info.add_argument(*self.password.args, **self.password.kwargs)
        self.info.add_argument(*self.repo.args, **self.repo.kwargs)
        self.info.add_argument(*self.tag.args, **self.tag.kwargs)
        self.info.add_argument(*self.json.args, **self.json.kwargs)
        self.info.add_argument(*self.latest.args, **self.latest.kwargs)
        # TODO: assets and tag are grouped
        self.info.add_argument(*self.assets.args, **self.assets.kwargs)
                
            #release:
        self.release = self.subparsers.add_parser('release', help='Release a release or a tag')
        self.release.add_argument(*self.security_token.args, **self.security_token.kwargs)
        self.release.add_argument(*self.owner.args, **self.owner.kwargs)
        self.release.add_argument(*self.user.args, **self.user.kwargs)
        self.release.add_argument(*self.password.args, **self.password.kwargs)
        self.release.add_argument(*self.repo.args, **self.repo.kwargs)
        self.release.add_argument(*self.tag.args, **self.tag.kwargs)
        self.release.add_argument(*self.name.args, **self.name.kwargs)
        self.release.add_argument(*self.description.args, **self.description.kwargs)
        self.release.add_argument(*self.target.args, **self.target.kwargs)
        self.release.add_argument(*self.draft.args, **self.draft.kwargs)
        self.release.add_argument(*self.pre_release.args, **self.pre_release.kwargs)
            
            #upload:
        self.upload = self.subparsers.add_parser('upload', help='Upload a release or a tag')
        self.upload.add_argument(*self.security_token.args, **self.security_token.kwargs)
        self.upload.add_argument(*self.owner.args, **self.owner.kwargs)
        self.upload.add_argument(*self.user.args, **self.user.kwargs)
        self.upload.add_argument(*self.password.args, **self.password.kwargs)
        self.upload.add_argument(*self.repo.args, **self.repo.kwargs)
        self.upload.add_argument(*self.tag.args, **self.tag.kwargs)
        self.upload.add_argument(*self.name.args, **self.name.kwargs)
        self.upload.add_argument(*self.label.args, **self.label.kwargs)
        self.upload.add_argument(*self.file.args, **self.file.kwargs)
        self.upload.add_argument(*self.replace.args, **self.replace.kwargs)
        
    def handle_args(self, args=None):
        self._args = self.parser.parse_args(args)
        
if __name__ == '__main__':

    #####################
    # Argument handling #
    #####################

    args = ArgHandler(prog="GitHub Publish", version=__version__)
    args.handle_args()