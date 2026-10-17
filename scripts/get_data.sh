#!/usr/bin/env bash
# Tải 8 file CSV của bộ dữ liệu Olist vào data/raw/
# Nguồn gốc: Kaggle "Brazilian E-Commerce Public Dataset by Olist" (giấy phép CC BY-NC-SA 4.0)
#   https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# Có thể tải trực tiếp từ Kaggle, hoặc dùng bản sao trên GitHub như dưới đây.
set -e
cd "$(dirname "$0")/.."
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/spdrio/Brazilian-E-Commerce-Public-Dataset-by-Olist.git "$tmp/olist"
mkdir -p data/raw
cp "$tmp"/olist/files/*.csv data/raw/
rm -rf "$tmp"
ls data/raw
