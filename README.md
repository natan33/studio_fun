# 🚀 Studio Fun - Gestão Fitness Integrada

O **Studio Fun** é um sistema de gestão completo para studios de fitness e academias. O projeto foca na automatização de cobranças, controle de matrículas e comunicação eficiente com o aluno através de e-mails automatizados e um dashboard intuitivo.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.x com [Flask](https://flask.palletsprojects.com/)
* **Banco de Dados:** PostgreSQL / SQLAlchemy (ORM)
* **Fila de Tarefas:** [Celery](https://docs.celeryq.dev/) com Redis
* **Frontend:** Bootstrap 5, Jinja2 e FontAwesome
* **Segurança:** Flask-Login e Werkzeug para hashing de senhas
* **E-mail:** Flask-Mail com templates HTML customizados

## 🌟 Funcionalidades Principais

* **Gestão de Planos:** Criação de ciclos personalizados (Quinzenal, Mensal, Anual, etc.).
* **Matrícula Inteligente:** Vinculação automática de aluno, plano e turma.
* **Automação de E-mails:**
    * Boas-vindas personalizado com cronograma de aulas.
    * Envio de faturas com QR Code PIX (Dark Style).
    * Trava de segurança (Log) para evitar envios duplicados.
* **Cobrança Automática:** Jobs agendados para verificar vencimentos e gerar faturas.
* **Dashboard Administrativo:** Controle total de alunos e turmas.

## 🚀 Como Executar o Projeto

### 1. Clonar o repositório
```bash
git clone [https://github.com/seu-usuario/studio-fun.git](https://github.com/seu-usuario/studio-fun.git)
cd studio-fun
```

### 2. Configurar o Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente (.env)
```bash
FLASK_APP=run.py
SECRET_KEY=sua_chave_secreta
DATABASE_URL=postgresql://user:password@localhost/studio_fun
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
REDIS_URL=redis://localhost:6379/0
```
