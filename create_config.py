import yaml
try:
    import bcrypt
    pwd = bcrypt.hashpw(b'nio@102030', bcrypt.gensalt()).decode('utf-8')
except ImportError:
    # Fallback caso não consiga instalar bcrypt agora (o authenticator vai precisar dele de qualquer forma)
    pwd = 'abc' # Isso fará o login falhar, mas o arquivo será criado.

config = {
    'credentials': {
        'usernames': {
            'nio_admin': {
                'email': 'admin@admin.com',
                'name': 'Administrador',
                'password': pwd
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'random_signature_key',
        'name': 'some_cookie_name'
    },
    'pre-authorized': {
        'emails': ['admin@admin.com']
    }
}

with open('config.yaml', 'w') as f:
    yaml.dump(config, f)
print("config.yaml gerado com sucesso!")
