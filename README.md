# RainDrop (Python + Flet)

채움으로 삶의 밀도를 기록한다 — 크로스플랫폼 집중 타이머 앱

## 실행

```bash
pip install -r requirements.txt
python main.py
```

## Windows exe 빌드

```bash
pip install flet
flet pack main.py --name RainDrop --icon icon.png
```

결과: `dist/RainDrop.exe`

## 시스템 요구사항

- Python 3.10 이상
- 또는 빌드된 exe (Python 불필요)
