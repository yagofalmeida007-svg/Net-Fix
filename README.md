# 🛠️ NetFix

### Diagnóstico e otimização de conexão de rede para Windows

O **NetFix** é um aplicativo desktop desenvolvido em Python, com o objetivo de diagnosticar problemas de conexão com a internet, identificar instabilidades e oferecer ferramentas para auxiliar na manutenção da rede.

O projeto busca oferecer uma interface moderna, intuitiva e acessível, reunindo ferramentas de diagnóstico em um único lugar.

> 🚧 **Status:** Em desenvolvimento.

---

## 🎯 Objetivo do projeto

Desenvolver uma ferramenta capaz de ajudar usuários a identificar problemas de conexão, como:

- Ping elevado.
- Perda de pacotes.
- Instabilidade na conexão.
- Problemas de resolução DNS.
- Variações no tempo de resposta (jitter).

O NetFix também pretende oferecer ferramentas de reparo e monitoramento de rede.

## ✨ Funcionalidades

### Implementadas
- [x] Interface gráfica com tema escuro.
- [x] Teste de conectividade utilizando ping.
- [x] Cálculo de ping médio.
- [x] Cálculo de perda de pacotes.
- [x] Estimativa de jitter.
- [x] Diagnóstico básico de DNS (em desenvolvimento).

### Planejadas
- [ ] Monitoramento de conexão em tempo real.
- [ ] Histórico de diagnósticos.
- [ ] Identificação automática de problemas.
- [ ] Ferramentas de reparo de rede.
- [ ] Limpeza de cache DNS.
- [ ] Renovação de endereço IP.
- [ ] Geração de relatórios.
- [ ] Sistema de licenciamento.
- [ ] Versão gratuita e versão Pro.

## 💻 Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| Python | Linguagem principal |
| CustomTkinter | Interface gráfica |
| Psutil | Informações do sistema e rede |
| Matplotlib | Gráficos e monitoramento |
| Socket | Testes de conectividade |
| Subprocess | Execução de comandos do Windows |

## 📁 Estrutura do projeto

```text
NetFix/
│
├── main.py
├── requirements.txt
│
├── interface/
│   ├── __init__.py
│   └── dashboard.py
│
├── services/
│   ├── __init__.py
│   ├── diagnostico.py
│   ├── conexao.py
│   └── reparo.py
│
├── utils/
│   └── __init__.py
│
└── assets/
    ├── images/
    └── icons/
```

*Estrutura prevista para a evolução do projeto. Alguns arquivos e módulos ainda serão desenvolvidos.*

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone URL_DO_SEU_REPOSITORIO
```

### 2. Entre na pasta do projeto

```bash
cd NetFix
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

Caso ainda não tenha criado o arquivo `requirements.txt`, instale as bibliotecas utilizadas:

```bash
pip install customtkinter psutil matplotlib
```

### 4. Execute o aplicativo

```bash
python main.py
```

## 📊 Como funciona o diagnóstico

O NetFix realiza testes de conectividade utilizando pacotes ICMP para coletar informações como:

- **Ping:** tempo de resposta entre o computador e o servidor.
- **Perda de pacotes:** percentual de pacotes que não receberam resposta.
- **Jitter estimado:** variação média entre tempos de respostas consecutivas.

Os testes de DNS ajudam a verificar a resolução de nomes de domínio e a resposta de servidores DNS públicos.

**Observação:** resultados de ping e perda de pacotes podem variar conforme o servidor testado e o tratamento de tráfego ICMP pela rede.

## 🔐 Segurança

O projeto tem como objetivo executar diagnósticos de forma segura e transparente.

As futuras ferramentas de reparo deverão informar ao usuário quais alterações serão realizadas, solicitar autorização quando necessário e evitar modificações desnecessárias nas configurações do sistema.

## 🚀 Desenvolvimento

O NetFix está sendo desenvolvido gradualmente, com foco em:

1. Diagnóstico confiável.
2. Interface moderna.
3. Organização do código.
4. Segurança das operações.
5. Facilidade de utilização.

## 👨‍💻 Autor

**Yago Fernandes de Almeida**

Estudante de Ciência da Computação e desenvolvedor em formação, interessado em programação, tecnologia e desenvolvimento de soluções de software.

## 📄 Licença

Projeto em desenvolvimento. A licença de distribuição e utilização será definida futuramente.
