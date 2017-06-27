import json
import os
from optparse import OptionParser
import requests
import sys
import logging as log
import urllib
from pprint import pprint


from arg_parser import ArgHandler
__author__ = 'ravi'

# API urls for github
# www.github.com
API_URL = 'https://api.{}/repos/{}/{}/releases'
UPLOAD_URL = 'https://uploads.{}/repos/{}/{}/releases'
DOWNLOAD_URL = 'https://{}/{}/{}/releases'

# github.enterprise.com
ENTERPRISE_API_URL = '{}/api/v3/repos/{}/{}/releases'
ENTERPRISE_UPLOAD_URL = '{}/api/uploads/repos/{}/{}/releases'
ENTERPRISE_DOWNLOAD_URL = '{}/{}/{}/releases/download'

class GitHubPublish(object):
    """ GitHub publisher is used to manage tags and releases on *.github.com
    
    """
    def __init__(self, security_token, owner, repo, user=None, password='x-oauth-basic', proxy='', server='github.com'):  #=urllib.getproxies()

        self.server = 'github.com' if server is None else server
        self.security_token = security_token
        self.owner = owner
        self.user = self.security_token if user is None and self.security_token is not None else user
        self.password = password if password is not None else 'x-oauth-basic'
        self.repo = repo

        # url
        url = API_URL if server is None else ENTERPRISE_API_URL
        self.url = url.format(self.server, self.owner, self.repo)
        
        #upload_url
        upload_url = UPLOAD_URL if server is None else ENTERPRISE_UPLOAD_URL
        self.upload_url = upload_url.format(self.server, self.owner, self.repo)
        # download_url
        download_url = DOWNLOAD_URL if server is None else ENTERPRISE_DOWNLOAD_URL
        self.download_url = download_url.format(self.server, self.owner, self.repo)
        
        self.proxy = ''
        proxy_list = dict()
        if proxy is not None:
            proxy_list['http'] = proxy if proxy.startswith('http://') else ''
            proxy_list['https'] = proxy if proxy.startswith('https://') else ''
            self.proxy = proxy_list
        
        # print(self.url, self.security_token, self.owner, self.repo, self.user, self.password, self.upload_url, self.proxy)
        

    def _list_releases(self):
        """List releases for a repository
        
        GET /repos/:owner/:repo/releases
        """
        
        response = requests.get(self.url, proxies=self.proxy, auth=(self.user, self.password))
        releases = json.loads(response.text) 
        #pprint(releases)
        return releases
        
    def info_releases (self, tag_name=None, latest=None, assets=None, export=None):
        if assets and tag_name:
            result = self.list_assets_for_release_id(tag_name)
        elif tag_name:
            result =  self._get_release_by_tag(tag_name)
        elif latest:
            result = self._get_latest_release()
        else:
            result = self._list_releases()
        
        # Save it to file
        if export is not None:
            self._export(export, result)
        else:
            pprint(result)
        return result
    
    def _get_release_by_id(self, release_id):
        """Get a single release
        
        GET /repos/:owner/:repo/releases/:id
        """
        
        response = requests.get(
            '{}/{}'.format(self.url, release_id),
            proxies=self.proxy, 
            auth=(self.user, self.password)
        )   
        release_by_id = json.loads(response.text)
        #pprint(release_by_id)
        return release_by_id
    
    def _get_release_by_tag(self, tag_name):
        """Get a release by tag name

        GET /repos/:owner/:repo/releases/tags/:tag
        """
        
        response = requests.get(
            '{}/tags/{}'.format(self.url, tag_name), 
            proxies=self.proxy, 
            auth=(self.user, self.password)
        )
        release_by_tag = json.loads(response.text)
        return release_by_tag

    def _get_latest_release(self):
        """Get the latest release
        
        GET /repos/:owner/:repo/releases/latest 
        """
        
        response = requests.get(
            '{}/latest'.format(self.url),
            proxies=self.proxy, 
            auth=(self.user, self.password)
        )
        latest = json.loads(response.text)
        #pprint(latest)
        return latest
    
    def _get_latest_release_tag(self):
        tag_name = self._get_latest_release()['tag_name']
        return tag_name
    
    def _get_release_id(self, tag_name):
        all_releases = self._list_releases()
        for release in all_releases:
            if release.get('tag_name') == tag_name:
                return release.get('id')
        return None
    
    def _get_asset_id(self, tag_name, file):
        found_file = None
        file_name = file.split(os.sep)[-1]
        values = self._get_release_by_tag(tag_name)
        for assets in values['assets']:
            for key, asset in assets.items():
                if file_name in str(asset):
                    found_file = assets['id']
        return found_file
            
        
    def _create_release(self, tag_name, name=None, description=None, draft=False, pre_release=False, target=None):
        """Create a releaseIntegrations Enabled
        
        Users with push access to the repository can create a release.
        POST /repos/:owner/:repo/releases
        """
        
        target = "master" if target is None else target
        
        data = {
            "tag_name": tag_name,
            "target_commitish": target,
            "name": name if name else tag_name,
            "body": description if description else tag_name,
            "draft": bool(draft),
            "prerelease": bool(pre_release)
        }
        json_data = json.dumps(data)
        response = requests.post(
            self.url,
            proxies=self.proxy,
            data=json_data,
            auth=(self.user, self.password)
        )
        json_response = json.loads(response.text)
        if 'errors' in json_response or 'message' in json_response:
            log.error(response.text)
            return False
        else:
            print("Successfully created release {} for {}".format(tag_name, self.repo))
            return True
    
    def _edit_release(self, tag_name, name=None, description='', draft=False, pre_release=False, target='master'):
        """Edit a release
        
        Users with push access to the repository can edit a release.
        PATCH /repos/:owner/:repo/releases/:id
        """
        release_id = self._get_release_id(tag_name)
        target = 'master' if target is None else target
        data = {
            "tag_name": tag_name,
            "target_commitish": target,
            "name": name if name else tag_name,
            "body": description if description else tag_name,
            "draft": bool(draft),
            "prerelease": bool(pre_release)
        }
        json_data = json.dumps(data)
        response = requests.patch(
            '{}/{}'.format(self.url, release_id),
            proxies=self.proxy,
            data=json_data,
            auth=(self.user, self.password)
        )
        json_response = json.loads(response.text)
        if 'errors' in json_response or 'message' in json_response:
            log.error(response.text)
            return False
        else:
            print("Successfully edited the release {} for {}".format(tag_name, self.repo))
            return True
    
    def release(self, tag_name, name=None, description=None, draft=False, pre_release=False, target=None):
        """ Create or edit release details
        
        Users with push access to the repository can create a release.
        Create
            POST /repos/:owner/:repo/releases
        Edit
            PATCH /repos/:owner/:repo/releases/:id
        """
        if self._get_release_by_tag(tag_name)['tag_name'] == tag_name:
            self._edit_release(tag_name, name, description, draft, pre_release, target)
        else:
            self._create_release(tag_name, name, description, draft, pre_release, target)
    
    def delete_release(self, tag_name):
        """Delete a release
        
        DELETE /repos/:owner/:repo/releases/:id
        """
        release_id = self._get_release_id(tag_name)
        if not release_id:
            log.error("Could not find release for tag name: {}".format(tag_name))
            return False
        response = requests.delete(
            '{}/{}'.format(self.url, release_id),
            proxies=self.proxy,
            auth=(self.user, self.password)
        )
        response.raise_for_status()
        print("Successfully deleted release {}".format(tag_name))
        return True
        
    def list_assets_for_release_id(self, tag_name):
        """List assets for a release
        
        GET /repos/:owner/:repo/releases/:id/assets
        """
        
        release_id = self._get_release_id(tag_name)
        assets_url = '{}/{}/assets'.format(self.url, release_id)
        response = requests.get(
            assets_url,
            proxies=self.proxy, 
            auth=(self.user, self.password)
        )
        assets = json.loads(response.text)
        #pprint(assets)
        return assets
    
    def push (self, method, url, data=None, file=None, label=None, headers=None):
        f = open('{}'.format(file,), 'rb') if file is not None else None
        data = f if f is not None else data
        response = getattr(requests, method)(
            url,
            proxies=self.proxy,
            data=data,
            headers={'Content-Type': 'application/x-tar'} if headers is None else headers,
            auth=(self.user, self.password)
        )
        f.close() if f is not None else None
        # pprint(response.text)
        json_response = json.loads(response.text)
        if 'errors' in json_response or 'message' in json_response:
            log.error(method + '\n' + response.text)
            return False
        else:
            response.raise_for_status()
            print('Successfully ' + method + ' asset {} to {}'.format(file, url))
            return True

    def _upload_release_asset(self, tag_name, file, label):
        """Upload a release asset
        
        POST https://<upload_url>/repos/:owner/:repo/releases/:id/assets?name=foo.zip

        """

        file_name = file.split(os.sep)[-1]
        release_id = self._get_release_id(tag_name)
        # TODO: Cannot upload with label, tried it with all re
        # Info: '{}/{}/assets?name={}' - this is the only pattern that works, but label=null and asset cannot be edited
        # "upload_url": "http://server.com/api/uploads/repos/user/test/releases/36/assets{?name,label}"
        # '{}/{}/assets{{?name={},label={}}}' - by the upload_url provided by enterprise server
        # and other variations
        # '{}/{}/assets{{?{},{}}}'
        # '{}/{}/assets?name={},label={}'
        
        upload_url = '{}/{}/assets?name={}'.format(self.upload_url, release_id, file_name)
        # print('upload_url', upload_url)
        return self.push('post', 
            upload_url,
            file=file,
            label=label,
            headers={'Content-Type': 'application/x-tar'}
        )

    def _edit_release_asset(self, tag_name, file, label, replace=False, asset_id=None):
        """Edit a release asset
        
        Users with push access to the repository can edit a release asset.
        PATCH /repos/:owner/:repo/releases/assets/:id
        """
        
        release_id = self._get_release_id(tag_name)
        edit_url = '{}/assets/{}'.format(self.url, asset_id)
        # print('edit_url', edit_url)
        return self.push('patch', 
            edit_url, 
            file=file,
            headers={'Content-Type': 'application/x-tar'}
        )
    
    def upload (self, tag_name, file, label, replace=False):
        asset_id = self._get_asset_id(tag_name, file)
        if asset_id is not None:
            self._edit_release_asset(tag_name, file, label, replace, asset_id)
        else:
            self._upload_release_asset(tag_name, file, label)
            
        
    def _get_release_asset(self, tag_name, artifact_name, latest=False):
        """Get a single release asset
        
        GET /repos/:owner/:repo/releases/assets/:id
        """
        tag_name = self._get_latest_release_tag() if latest else tag_name
        release_id = self._get_release_id(tag_name)
        asset_url = '{}/{}/{}'.format(self.download_url, tag_name, artifact_name)
        asset_response = requests.get(
            url=asset_url,
            proxies=self.proxy,
            headers={'Accept': 'application/octet-stream'},
            auth=(self.user, self.password)
        )
        with open(artifact_name, 'wb') as f:
            if asset_response.text == 'Not Found':
                log.error(asset_response.text + ' -> {}, {}'.format(tag_name, artifact_name))
                return False
            else:
                asset_response.raise_for_status()
                for block in asset_response.iter_content(1024):
                    if not block:
                        break
                    f.write(block)
        return True
    
    def _get_release_assets(self, tag_name, latest=False):
        tag_name = self._get_latest_release_tag() if latest else tag_name
        release_id = self._get_release_id(tag_name)
        assets_url = '{}/{}/assets'.format(self.url, release_id)
        assets_response = requests.get(url=assets_url, proxies=self.proxy, auth=(self.user, self.password))
        assets = json.loads(assets_response.text)
            
        for asset in assets:
            artifact_name = asset['name']
            with open(artifact_name, 'wb') as f:
                asset_url = ' {}/{}/{}'.format(self.download_url, tag_name, artifact_name)
                asset_response = requests.get(
                    url=asset_url,
                    proxies=self.proxy,
                    headers={'Accept': 'application/octet-stream'},
                    auth=(self.user, self.password))
                
                json_response = json.loads(assets_response.text)
                if 'errors' in json_response or 'message' in json_response:
                    log.error(asset_response.text + ' -> {}, {}'.format(tag_name, artifact_name))
                else:
                    asset_response.raise_for_status()
                    for block in asset_response.iter_content(1024):
                        if not block:
                            break
                        f.write(block)
    
    def download(self, tag_name, artifact_name, download_all=None, latest=None):
        if latest:
            print('Assets will be downloaded from latest release and not from {}'.format(tag_name))
            
        if download_all:
            self._get_release_assets(tag_name, latest)
        else:
            self._get_release_asset(tag_name, artifact_name, latest)

    def list_release_assets(self, tag_name, export=None):
        release_id = self.get_release_id(tag_name)
        artifacts = requests.get('{}/{}/assets?'.format(self.url, release_id), proxies=self.proxy, 
                                 auth=(self.user, self.password))
        result = json.loads(artifacts.text)
        if export is not None:
            self._export(export, result)
        #pprint(result)
    
    def _export (self, file_name, data, export_type='json'):
        if file_name is not None:
            if export_type == 'json':
                with open(file_name, 'w') as f:
                    json.dump(data, f, indent=4, sort_keys=True)

def main():
    # Init parser
    parser = ArgHandler(prog='GitHubPublisher')
    
    # Check if arguments are provided
    if len(sys.argv) <= 1:
        print(parser.help)
        sys.exit(-1)
    
    # Get arguments
    args = parser.parser.parse_args()
    
    # Init GitHubPublisher
    gh_release = GitHubPublish(args.security_token, args.owner, args.repo, args.user, args.password, args.proxy, args.server)

    try:
        if args.subcommand == 'info':
            result = gh_release.info_releases(args.tag_name, args.latest, args.assets, args.json)
        elif args.subcommand == 'release':
            result = gh_release.release(args.tag_name, name=args.name, description=args.description, pre_release=args.pre_release, target=args.target)
        elif args.subcommand == 'delete':
            for i in range(250, 280):  # what are these magic numbers?
                try:
                    result = gh_release.delete_release(args.tag_name)
                except:
                    pass
        elif args.subcommand =='edit':
            result = gh_release.edit_release(args.tag_name, args.file, args.label, args.replace)
        elif args.subcommand =='upload':
            result = gh_release.upload(args.tag_name, args.file, args.label, args.replace)
        elif args.subcommand =='download':
            result = gh_release.download(args.tag_name, args.name, args.download_all)
        else:
            result = gh_release._list_releases()
            print('Releases: {}'.format(str(result)))
        
        if result:
           sys.exit()
        else:
            sys.exit(-2)
    except Exception as exc:
        log.error(exc.message)
        sys.exit(-2)
    
if __name__ == "__main__":
    main()