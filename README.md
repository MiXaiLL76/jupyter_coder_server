# jupyter_code_server

## Disclaimer

Многие разработчики вынужденны пользоваться jupyterlab\\jupyterhub во время работы, без возможности спользовать VSCODE.
Наши товарищи из [coder](https://github.com/coder) проделали огромную работу, чтобы была возможность пользоваться VSCODE через браузер.
Моя работа осталось за малым, подружить эти две технологии и дать возможность быстро и удобно запускать оба этих приложения.

Эта библиотека работает в паре с библиотекой [jupyter-server-proxy](https://github.com/jupyterhub/jupyter-server-proxy), которая в свою очередь позволяет создавать внутри Jupyter дополнительные сервера.

## Install

Просто запустите установку из pypi и наслаждайтесь

```bash
pip install jupyter_code_server
```

После установки, обязательно перезапустите сервер (если он запущен в docker, то перезапуск docker)

## Requirements

Для более подробной информации [посмотрите тут](https://github.com/coder/code-server?tab=readme-ov-file#requirements)

## License

Так как проект [code-server](https://github.com/coder/code-server) имеет MIT лицензию, в этом проекте я ее тоже применяю.

## Citation

```
@article{jupyter_code_server,
  title   = {{jupyter_code_server}: VSCODE integration in jupyter-lab},
  author  = {MiXaiLL76},
  year    = {2024}
}
```
