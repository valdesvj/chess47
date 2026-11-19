#!/bin/sh
# setup.sh - build f42run, a headless Free42 (SwissMicros' core, the core of the DM42 / DM42n stock firmware) with
# the DM42 400 x 240 graphics, for the tests of the Free42 build of Chess 47 (tools/build_free42.py).
# Unlike almanac47's tools/f42 (binary doubles), this one is the DECIMAL Free42 (Intel's decimal library, 34 digits):
# the calculator's arithmetic, so WSIZE 64 words (the knight masks) are exact.
#   sh tools/f42/setup.sh        -> tools/f42/f42run          (downloads about 8 MB, builds in a few minutes)
# Free42 is (c) Thomas Okken, GPL v2; Intel's library: BSD; this script and f42run.cc: GPL v3 or later (Chess 47).
set -e
D=$(cd "$(dirname "$0")" && pwd)
W="$D/src"
mkdir -p "$W/common" "$W/windows" "$W/lib"
U=https://raw.githubusercontent.com/swissmicros/free42/master
for f in core_aux.cc core_aux.h core_commands1.cc core_commands1.h core_commands2.cc core_commands2.h \
         core_commands3.cc core_commands3.h core_commands4.cc core_commands4.h core_commands5.cc core_commands5.h \
         core_commands6.cc core_commands6.h core_commands7.cc core_commands7.h core_display.cc core_display.h \
         core_globals.cc core_globals.h core_helpers.cc core_helpers.h core_keydown.cc core_keydown.h \
         core_linalg1.cc core_linalg1.h core_linalg2.cc core_linalg2.h core_main.cc core_main.h \
         core_math1.cc core_math1.h core_math2.cc core_math2.h core_phloat.cc core_phloat.h \
         core_sto_rcl.cc core_sto_rcl.h core_tables.cc core_tables.h core_variables.cc core_variables.h \
         free42.h shell.h shell_spool.cc shell_spool.h bid_conf.h bid_functions.h; do
  [ -f "$W/common/$f" ] || curl -sSf -o "$W/common/$f" "$U/common/$f"
done
[ -f "$W/windows/VERSION.h" ] || curl -sSf -o "$W/windows/VERSION.h" "$U/windows/VERSION.h"
# Intel's decimal library, built as Free42's gtk/build-intel-lib.sh does
if [ ! -f "$W/lib/gcc111libbid.a" ]; then
  cd "$W/lib"
  [ -f IntelRDFPMathLib20U1.tar.gz ] || curl -sSf -o IntelRDFPMathLib20U1.tar.gz "$U/inteldecimal/IntelRDFPMathLib20U1.tar.gz"
  [ -f intel-lib-linux.patch ] || curl -sSf -o intel-lib-linux.patch "$U/gtk/intel-lib-linux.patch"
  rm -rf IntelRDFPMathLib20U1 && tar xfz IntelRDFPMathLib20U1.tar.gz
  cd IntelRDFPMathLib20U1 && patch -s -p0 < ../intel-lib-linux.patch && cd LIBRARY
  make -s CC=gcc CALL_BY_REF=1 GLOBAL_RND=1 GLOBAL_FLAGS=1 UNCHANGED_BINARY_FLAGS=0 >/dev/null 2>&1
  mv libbid.a ../../gcc111libbid.a
fi
cd "$W/common"
# the DM42 graphics (GrMod, 400 x 240, AGRAPH modes) without the rest of the ARM build
for f in core_aux.cc core_display.cc core_commands7.cc shell.h; do
  sed -i 's/#ifdef ARM$/#if defined(ARM) || defined(F42GR)/; s/#if defined(ARM)$/#if defined(ARM) || defined(F42GR)/; s/#ifndef ARM$/#if !defined(ARM) \&\& !defined(F42GR)/' $f
done
# f42run's hook: GETKEYA with no key waiting (the program polls: the test script goes on)
grep -q f42_getkeya core_commands7.cc || sed -i 's/    int key = dequeue_key();/    int key = dequeue_key(); extern void f42_getkeya(int); f42_getkeya(key);/' core_commands7.cc
n=$(grep -n 'cmdnam2buf(buf, len, &bufptr, cmdspec->name' core_display.cc | cut -d: -f1)
[ -n "$n" ] && sed -i "$((n-1))s/.*/#ifdef ARM/" core_display.cc
g++ -std=c++11 -w -O2 -DF42GR -DBCD_MATH -DDECIMAL_CALL_BY_REFERENCE=1 -DDECIMAL_GLOBAL_ROUNDING=1 \
    -DDECIMAL_GLOBAL_ROUNDING_ACCESS_FUNCTIONS=1 -DDECIMAL_GLOBAL_EXCEPTION_FLAGS=1 \
    -DDECIMAL_GLOBAL_EXCEPTION_FLAGS_ACCESS_FUNCTIONS=1 -DHAVE_SINCOS=1 -D_WCHAR_T_DEFINED \
    -include ctype.h -include core_variables.h -I. *.cc "$D/f42run.cc" "$W/lib/gcc111libbid.a" -o "$D/f42run" -lm
echo "built $D/f42run (decimal)"
