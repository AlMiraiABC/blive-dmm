FROM python:3.10.4-alpine
LABEL author="almirai"
LABEL email="live.almirai@outlook.com"
LABEL version="0.1"
LABEL description="bilibili live danmaku management."
LABEL name="blive-dmm"
COPY . /blive-dmm
WORKDIR /blive-dmm
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /blive-dmm
RUN python -m pip install --no-cache-dir -U -i https://pypi.tuna.tsinghua.edu.cn/simple pip && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
USER appuser
CMD python app.py
