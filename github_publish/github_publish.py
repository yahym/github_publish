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

API_URL = 'https://api.{}/repos/{}/{}/releases'
UPLOAD_URL = 'https://uploads.{}/repos/{}/{}/releases'
DOWNLOAD_URL = 'https://{}/{}/{}/releases'


class GitHubPublish(object):
    """ GitHub publisher is used to manage tags and releases on *.github.com
    
    """
    def __init__(self, security_token, owner, repo, user=None, password='x-oauth-basic', proxy=None, server='github.com'):  #=urllib.getproxies()
        
        self.security_token = security_token
        self.owner = owner
        self.user = self.security_token if user is None and self.security_token is not None else user
        self.password = password if password is not None else 'x-oauth-basic'
        self.repo = repo
        self.url = API_URL.format(server, self.owner, self.repo)
        self.upload_url = UPLOAD_URL.format(server, self.owner, self.repo)
        self.download_url = DOWNLOAD_URL.format(server, self.owner, self.repo)
        proxy_list = dict()
        proxy_list['http'] = proxy
        proxy_list['https'] = proxy
        self.proxy = proxy_list if proxy is not None else None
        
        # print(self.url, self.security_token, self.owner, self.repo, self.user, self.password, self.upload_url, self.proxy)
        # print(requests.get('https://api.github.com/repos/umihai1/test/releases', proxies=self.proxy))
    

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
            result =  self.get_release_by_tag(tag_name)
        elif latest:
            result = self._get_latest()
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
        
    def _get_latest(self):
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
        #pprint(release_by_tag)
        return release_by_tag

    def create_release(self, tag, name=None, description=None, draft=False, prerelease=False, target=None):
        """Create a releaseIntegrations Enabled
        
        POST /repos/:owner/:repo/releases
        """
        
        target = "master" if target is None else target
        data = {
            "tag_name": tag,
            "target_commitish": target,
            "name": name if name else tag,
            "body": description if description else tag,
            "draft": bool(draft),
            "prerelease": bool(prerelease)
        }
        json_data = json.dumps(data)
        response = requests.post(
            self.url,
            proxies=self.proxy,
            data=json_data,
            auth=(self.user, self.password)
        )
        json_response = json.loads(response.text)
        if json_response.get('errors') or json_response.get('message'):
            log.error(response.text)
            return False
        else:
            print("Successfully created release {} for {}".format(tag, self.repo))
            return True
    
    def edit_release(self, tag_name, target=None, name=None, description='', draft=False, pre_release=False):
        """Edit a release
        
        PATCH /repos/:owner/:repo/releases/assets/:id
        """
        release_id = self._get_release_id(tag_name)
        target = "master" if target is None else target
        data = {
            "tag_name": tag,
            "target_commitish": target,
            "name": name if name else tag,
            "body": description if description else tag,
            "draft": bool(draft),
            "prerelease": bool(prerelease)
        }
        json_data = json.dumps(data)
        response = requests.post(
            '{}/assets/{}'.format(self.url, release_id),
            proxies=self.proxy,
            data=json_data,
            auth=(self.user, self.password)
        )
        json_response = json.loads(response.text)
        if json_response.get('errors') or json_response.get('message'):
            log.error(response.text)
            return False
        else:
            print("Successfully edited the release {} for {}".format(tag_name, self.repo))
            return True
        
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
        print(assets_url)
        response = requests.get(
            assets_url,
            proxies=self.proxy, 
            auth=(self.user, self.password)
        )
        assets = json.loads(response.text)
        #pprint(assets)
        return assets
    
    def upload_release_asset(self, tag_name, file, label, replace=True):
        """Upload a release asset
        
        POST https://<upload_url>/repos/:owner/:repo/releases/:id/assets?name=foo.zip   
        """
        release_id = self._get_release_id(tag_name)
        upload_url = '{}/{}/assets?name={}'.format(self.upload_url, release_id, label)
        f = open('{}'.format(file,), 'rb')
        if replace:
            self.edit_release_asset(tag_name, file, label)
        else:
            upload_response = requests.post(upload_url,
                proxies=self.proxy,
                data=f,
                headers={'Content-Type': 'application/x-tar'},
                auth=(self.user, self.password)
            )
            f.close()
            json_response = json.loads(upload_response.text)
            if json_response.get('errors') or json_response.get('message'):
                log.error(upload_response.text)
                return False
            else:
                upload_response.raise_for_status()
                print("Successfully uploaded asset {} for {}".format(file, tag_name))
                return True
    
    def _get_release_asset(self, tag_name, artifact_name):
        """Get a single release asset
        
        GET /repos/:owner/:repo/releases/assets/:id
        """
        release_id = self._get_release_id(tag_name)
        asset_url = ' {}/download/{}/{}'.format(self.download_url, tag_name, artifact_name)
        asset_response = requests.get(
            url=asset_url,
            proxies=self.proxy,
            headers={'Accept': 'application/octet-stream'},
            auth=(self.user, self.password)
        )
        with open(artifact_name, 'wb') as f:
            asset_response.raise_for_status()
            for block in asset_response.iter_content(1024):
                if not block:
                    break
                f.write(block)
        return True
    
    def _get_release_assets(self, tag_name):
        release_id = self._get_release_id(tag_name)
        assets_url = '{}/{}/assets'.format(self.url, release_id)
        assets_response = requests.get(url=assets_url, proxies=self.proxy, auth=(self.user, self.password))
        assets = json.loads(assets_response.text)
            
        for asset in assets:
            with open(asset['name'], 'wb') as f:
                asset_url = ' {}/download/{}/{}'.format(self.download_url, tag_name, asset['name'])
                asset_response = requests.get(
                    url=asset_url,
                    proxies=self.proxy,
                    headers={'Accept': 'application/octet-stream'},
                    auth=(self.user, self.password))
                asset_response.raise_for_status()

                for block in asset_response.iter_content(1024):
                    if not block:
                        break
                    f.write(block)
    
    def download(self, tag_name, artifact_name, download_all=None):
        if download_all:
            self._get_release_assets(tag_name)
        else:
            self._get_release_asset(tag_name, artifact_name)

    def edit_release_asset(self, tag_name, file, label):
        """Edit a release asset
        
        PATCH /repos/:owner/:repo/releases/assets/:id
        """
        
        release_id = self._get_release_id(tag_name)
        edit_url = '{}/{}/assets/{}'.format(self.upload_url, release_id, label)
        print(edit_url)
        f = open('{}'.format(file,), 'rb')
        edit_response = requests.patch(
            edit_url,
            proxies=self.proxy,
            data=f,
            headers={'Content-Type': 'application/x-tar'},
            auth=(self.user, self.password)
        )
        edit_response = json.loads(edit_response.text)
        if edit_response.get('errors') or edit_response.get('message'):
            log.error(edit_response.text)
            return False
        else:
            edit_response.raise_for_status()
            print("Successfully uploaded asset {} for {}".format(file, tag_name))
            return True
        

    def _get_release_id(self, tag_name):
        all_releases = self._list_releases()
        for release in all_releases:
            if release.get('tag_name') == tag_name:
                return release.get('id')
        return None
        
    
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

if __name__ == "__main__":

    # Init parser
    parser = ArgHandler(prog='GitHubPublisher')
    
    # Check if arguments are provided
    if len(sys.argv) <= 1:
        print(parser.help)
        sys.exit(-1)
    
    # Get arguments
    args = parser.parser.parse_args()
    
    # Init GitHubPublisher
    gh_release = GitHubPublish(args.security_token, args.owner, args.repo, args.user, args.password, args.proxy)
    
    try:
        if args.subcommand =='info':
            result = gh_release.info_releases(args.tag, args.latest, args.assets, args.json)
        elif args.subcommand =='release':
            result = gh_release.create_release(args.tag, args.name, args.description, args.pre_release, args.target)
        elif args.subcommand =='delete':
            for i in range(250, 280):  # what are these magic numbers?
                try:
                    result = gh_release.delete_release(args.tag)
                except:
                    pass
        elif args.subcommand =='edit':
            result = gh_release.edit_release(args.tag, args.file, args.label, args.replace)
        elif args.subcommand =='upload':
            result = gh_release.upload_release_asset(args.tag, args.file, args.label, args.replace)
        elif args.subcommand =='download':
            result = gh_release.download(args.tag, args.name, args.download_all)
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