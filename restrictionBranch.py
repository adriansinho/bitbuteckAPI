# Install
# ! pip install pyfunctional 

from functional import seq
import os
import requests


session = requests.Session()
session.auth = (os.environ['BB_USERNAME'], os.environ['BB_APP_PASSWORD'])
session.headers.update({'Content-Type': 'application/json'})

host = 'https://api.bitbucket.org/2.0/repositories'
apiBranchRestrictions = 'branch-restrictions'

workSpace = 'xxx'
branchsNames = ['master', 'develop']
fullRepoName = []

def getRestriction(branchName):
    return [
        {
            "kind": "push",      
            "branch_match_kind": "glob",
            "type": "branchrestriction",
            "groups": [      
                {
                    "type": "group",
                    "owner": {
                    "display_name": "Group_01",            
                    "type": "team",
                    "uuid": "{a3ac2d70-8143-4844-b72f-e588a30e5cef}",
                    "username": "group_01"
                    },
                    "slug": "ci",
                    "full_slug": "xxx:ci",
                    "name": "CI"
                }
            ],
            "pattern": branchName   
        },
        {
        "pattern": branchName,
        "kind": "restrict_merges",
        "branch_match_kind": "glob",
        "type": "branchrestriction",
        "groups": [
            {
            "type": "group",
            "owner": {
                "display_name": "Group_01",            
                "type": "team",
                "uuid": "{a3ac2d70-8143-4844-b72f-e588a30e5cef}",
                "username": "group_01"
            },          
            "slug": "developers",
            "full_slug": "xxx:developers",
            "name": "Developers"
            },
            {
            "type": "group",
            "owner": {
                "display_name": "Group_01",
                "type": "team",
                "uuid": "{a3ac2d70-8143-4844-b72f-e588a30efcef}",
                "username": "group_01"
            },
            "slug": "ci",
            "full_slug": "xxx:ci",
            "name": "CI"
            },
            {
            "type": "group",
            "account_privilege": "admin",
            "full_slug": "xxx:administrators",
            "name": "Administrators",
            "slug": "administrators",
            "owner": {
                "display_name": "adrian",            
                "type": "team",
                "uuid": "{a31c2d71-8143-4843-b72f-e231a3sascef}",
                "username": "adrian"
            }         
        }
        ]
        }
    ]


def getListRepos(workSpace):
    fullRepoListSlug = []
    # * Request 100 repositories per page and the next page URL
    nextPageUrl = 'https://api.bitbucket.org/2.0/repositories/%s?pagelen=10&fields=next,values.links.clone.href,values.slug' % workSpace        
    
    while nextPageUrl is not None:        
        response = session.get(nextPageUrl)
        pageJson = response.json()

        # * Parse repos JSON
        for repo in pageJson['values']:
            #print (repo['slug'])            
            fullRepoListSlug.append(repo['slug'])
            
        # * Next page 
        nextPageUrl = pageJson.get('next', None)
        
    return fullRepoListSlug


def deleteRestrictionBranch(workSpace,api,repo,branch):
    try:
        result = session.get(url=f'{host}/{workSpace}/{repo}/{api}')
        result.raise_for_status()
        data = result.json()
        ids = seq(data['values']) \
            .filter(lambda value: value.get('branch_match_kind') == 'glob') \
            .filter(lambda value: value.get('pattern') == branch) \
            .map(lambda value: value.get('id')) \
            .to_list()
        if ids:
            print(f'    Clearing {len(ids)} existing restrictions', end='\n', flush=True)
            for id in ids:
                result = session.delete(url=f'{host}/{workSpace}/{repo}/{api}/{id}')
                result.raise_for_status()    
    except:
        print('Something went wront - Delete :(', end='\n', flush=True)
    

def insertRestrictionBranch(workSpace,api,repo,branchRestrictions):    
    try:
        print(f'    Applying {len(branchRestrictions)} new restrictions', end='\n', flush=True)
        for branchRest in branchRestrictions:
            result = session.post(url=f'{host}/{workSpace}/{repo}/{api}', json=branchRest)
            result.raise_for_status()
    except:
        print('Something went wront - insert :(', end='\n', flush=True)

# ? --------------------
# ? Start de execution
# ? --------------------

fullRepoName = getListRepos(workSpace)

if len(fullRepoName)==0:
    exit 

for name in fullRepoName:
    if (name=='ci-testing'):
        for branch in branchsNames:
            print(f' Repo -> {name}             Branch -> {branch}', end='\n', flush=True)
            deleteRestrictionBranch(workSpace,apiBranchRestrictions,name,branch)
            insertRestrictionBranch(workSpace,apiBranchRestrictions,name,getRestriction(branch))
