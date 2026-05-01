from fastapi import FastAPI
from .api import auth, properties, users, bookings

app = FastAPI(title='Property Platform API')

app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(properties.router, prefix='/properties', tags=['properties'])
app.include_router(users.router, prefix='/users', tags=['users'])
app.include_router(bookings.router, prefix='/bookings', tags=['bookings'])

@app.get('/health')
def health():
    return {'status': 'ok'}
