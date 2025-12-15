# Python 3.10 versiyasini asos qilib olamiz (yengil versiya)
FROM python:3.10-slim

# Konteyner ichida ishchi papkani belgilaymiz
WORKDIR /app

# Atrof-muhit o'zgaruvchilari (loglarni to'g'ri ko'rish uchun)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Barcha kodlarni ko'chirib o'tkazamiz
COPY . .

# Botni ishga tushirish
CMD ["python", "main.py"]
