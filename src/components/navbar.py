
from dash import html, dcc

layout = html.Nav([
    dcc.Link('Home', href='/', className='nav-link'),
    dcc.Link('Informações do Aluno', href='/page1', className='nav-link'),
    dcc.Link('Informações Pessoais do Aluno', href='/page2', className='nav-link'),
], className='navbar')


