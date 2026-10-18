#!/usr/bin/env bash
# bilibili-id.sh — Bilibili video ID extraction; sourced by download-video.sh.
#
# Exposes:
#   bilibili_video_id <URL>  Prints bili-<BV>-p<N> (av ids are canonicalized
#                            to BV) or bili-ep... / bili-ss... for
#                            bangumi/cheese pages; exits nonzero when the URL
#                            is not a Bilibili video page. The part number is
#                            included so different parts of a multi-part
#                            video don't dedup to one file.
#   av_to_bv <av>            Canonical BV form of an av id.
#   bilibili_part <URL>      Part number from the p query parameter (default 1).
#
# Host matching is case-insensitive and the scheme is optional. Only the path
# is inspected, so query/fragment text can never fake a BV id.
#
# This file is a library: it sets no shell options and runs nothing on its own.

# Converts a Bilibili av id to its canonical BV id (Bilibili's public XOR
# mapping), so av and BV links to the same video share one file.
av_to_bv() {
  local table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
  local pos=(11 10 3 8 4 6)
  local x=$(( ($1 ^ 177451812) + 8728348608 ))
  local r='BV1  4 1 7  '
  local pow=1 i
  for ((i = 0; i < 6; i++)); do
    r="${r:0:${pos[i]}}${table:$((x / pow % 58)):1}${r:$((pos[i] + 1))}"
    pow=$((pow * 58))
  done
  echo "$r"
}

# Prints the Bilibili part number (the p query parameter); defaults to 1.
# Only a top-level p= in the query string counts, so values embedded in other
# parameters or the fragment are ignored; digits are capped at 9 so oversized
# values can't overflow the arithmetic.
bilibili_part() {
  local part=1 query="${1%%#*}"
  [[ "$query" == *\?* ]] && query="${query#*\?}" || query=""
  if [[ "$query" =~ (^|&)[pP]=([0-9]{1,9})($|&) ]]; then
    # 10# normalizes leading zeros; p=0 is not a valid part number.
    part=$((10#${BASH_REMATCH[2]}))
    (( part >= 1 )) || part=1
  fi
  echo "$part"
}

# Prints the Bilibili video ID from a URL: bili-<BV>-p<N> for video pages
# (av ids are canonicalized to BV), bili-ep... / bili-ss... for bangumi/cheese
# pages.
bilibili_video_id() {
  local url="${1%%#*}" host path
  url="${url%%\?*}"                      # match only scheme://host/path
  url="${url#*://}"                      # drop scheme if present (first //)
  host="${url%%/*}"
  host=$(tr '[:upper:]' '[:lower:]' <<< "$host")
  [[ "$host" == bilibili.com || "$host" == *.bilibili.com ]] || return 1
  path="${url#*/}"
  if [[ "$path" =~ ^video/(BV[0-9A-Za-z]{10})(/|$) ]]; then
    echo "bili-${BASH_REMATCH[1]}-p$(bilibili_part "$1")"
  elif [[ "$path" =~ ^video/[aA][vV]([0-9]{1,10})(/|$) ]]; then
    echo "bili-$(av_to_bv "$((10#${BASH_REMATCH[1]}))")-p$(bilibili_part "$1")"
  elif [[ "$path" =~ ^(bangumi|cheese)/play/(ep|ss)([0-9]+)(/|$) ]]; then
    echo "bili-${BASH_REMATCH[2]}${BASH_REMATCH[3]}"
  else
    return 1
  fi
}
