def deploy_netlfixy(zip_path, access_token)
  with open(zip_path, 'rb') as f:
    data = f.read()
  res = requests.post(url='https://api.netlify.com/api/v1/sites',
                      data=data,
                      headers={
                          'Content-Type': 'application/zip',
                          'Authorization': 'Bearer %s' % access_token,
                      })
  return res.json()['id']