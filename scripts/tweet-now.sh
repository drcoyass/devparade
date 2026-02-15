#!/bin/bash
# デブポジツイート即投稿スクリプト
# 使い方: bash scripts/tweet-now.sh
# ランダムなデブポジツイートを生成してブラウザで投稿画面を開く

TWEETS=(
"🍖【世界初】ポジデブBot、爆誕。SNS上の全ての「デブ」をポジティブに変換！総体重570kg超のバンド DEV PARADEが全力で肯定します。試してみて👇 https://dev-parade.github.io/debu-bot.html #ポジデブBot #DEVPARADE"
"デブは才能。脂肪は努力の結晶。俺たちDEV PARADE、メンバー全員90kg以上でメジャーデビューした。体重と才能は比例する。🍖 #ポジデブBot #DEVPARADE https://dev-parade.github.io/debu-bot.html"
"「太った」→「成長した」「デブ」→「存在感がある」「メタボ」→「ロックな体型」全部ポジティブに変換するBot作った🍖 https://dev-parade.github.io/debu-bot.html #ポジデブBot #DEVPARADE"
"体重と幸福度は比例する。（DEV PARADE調べ）source: 俺たち570kg超で幸せ🍖 #ポジデブBot #DEVPARADE https://dev-parade.github.io/debu-bot.html"
"NARUTOのエンディング歌ってたメンバー全員90kg以上のバンドが15年ぶりに復活して「デブをポジティブにするBot」を作った。全部事実です🍖 https://dev-parade.github.io/ #DEVPARADE #バッチコイ"
)

INDEX=$((RANDOM % ${#TWEETS[@]}))
TWEET="${TWEETS[$INDEX]}"

echo "🍖 デブポジツイート:"
echo ""
echo "$TWEET"
echo ""
echo "ブラウザで投稿画面を開きます..."

ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$TWEET'''))")
open "https://twitter.com/intent/tweet?text=$ENCODED"
