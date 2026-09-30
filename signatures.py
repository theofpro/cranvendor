GH = 'https://github.com/'

# lib -> (path regex, version regex or None, upstream repo, tag format)
LIBS = {
    'zlib': (
        r'(^|/)zlib\.h$',
        r'#define\s+ZLIB_VERSION\s+"([^"]+)"',
        GH + 'madler/zlib', 'v{}'),
    'sqlite': (
        r'(^|/)sqlite3\.h$',
        r'#define\s+SQLITE_VERSION\s+"([^"]+)"',
        GH + 'sqlite/sqlite', 'version-{}'),
    'libxml2': (
        r'(^|/)xmlversion\.h$',
        r'#define\s+LIBXML_DOTTED_VERSION\s+"([^"]+)"',
        'https://gitlab.gnome.org/GNOME/libxml2', 'v{}'),
    'expat': (
        r'(^|/)expat\.h$',
        r'XML_MAJOR_VERSION\s+(\d+)\s*\n#define\s+XML_MINOR_VERSION\s+(\d+)'
        r'\s*\n#define\s+XML_MICRO_VERSION\s+(\d+)',
        GH + 'libexpat/libexpat', 'R_{}'),
    'libpng': (
        r'(^|/)png\.h$',
        r'#define\s+PNG_LIBPNG_VER_STRING\s+"([^"]+)"',
        GH + 'pnggroup/libpng', 'v{}'),
    'libjpeg-turbo': (
        r'(^|/)jversion\.h$',
        r'#define\s+JVERSION\s+"([\d.]+)',
        GH + 'libjpeg-turbo/libjpeg-turbo', '{}'),
    'bzip2': (
        r'(^|/)bzlib_private\.h$',
        r'#define\s+BZ_VERSION\s+"([\d.]+)',
        'https://gitlab.com/bzip2/bzip2', 'bzip2-{}'),
    'lz4': (
        r'(^|/)lz4\.h$',
        r'LZ4_VERSION_MAJOR\s+(\d+).*?\n#define\s+LZ4_VERSION_MINOR\s+(\d+)'
        r'.*?\n#define\s+LZ4_VERSION_RELEASE\s+(\d+)',
        GH + 'lz4/lz4', 'v{}'),
    'zstd': (
        r'(^|/)zstd\.h$',
        r'ZSTD_VERSION_MAJOR\s+(\d+)\s*\n#define\s+ZSTD_VERSION_MINOR\s+(\d+)'
        r'\s*\n#define\s+ZSTD_VERSION_RELEASE\s+(\d+)',
        GH + 'facebook/zstd', 'v{}'),
    'pcre2': (
        r'(^|/)pcre2\.h(\.in|\.generic)?$',
        r'PCRE2_MAJOR\s+(\d+)\s*\n#define\s+PCRE2_MINOR\s+(\d+)',
        GH + 'PCRE2Project/pcre2', 'pcre2-{}'),
    'libuv': (
        r'(^|/)uv/version\.h$',
        r'UV_VERSION_MAJOR\s+(\d+)\s*\n#define\s+UV_VERSION_MINOR\s+(\d+)'
        r'\s*\n#define\s+UV_VERSION_PATCH\s+(\d+)',
        GH + 'libuv/libuv', 'v{}'),
    'yajl': (
        r'(^|/)yajl_version\.h$',
        r'YAJL_MAJOR\s+(\d+)\s*\n#define\s+YAJL_MINOR\s+(\d+)'
        r'\s*\n#define\s+YAJL_MICRO\s+(\d+)',
        GH + 'lloyd/yajl', '{}'),
    'cmark-gfm': (
        r'(^|/)cmark(-gfm)?_version\.h$',
        r'CMARK(?:_GFM)?_VERSION_STRING\s+"([^"]+)"',
        GH + 'github/cmark-gfm', '{}'),
    # version is in config.h, see scan.find_version
    'libxls': (r'(^|/)xls\.h$', None, GH + 'libxls/libxls', 'v{}'),
    'ReadStat': (r'(^|/)readstat\.h$', None, GH + 'WizardMac/ReadStat', 'v{}'),
    # FIXME: this picks up the R package version, not the C core
    'igraph': (
        r'(^|/)igraph_version\.h$',
        r'#define\s+IGRAPH_VERSION\s+"([^"]+)"',
        GH + 'igraph/igraph', '{}'),
    'mbedtls': (
        r'(^|/)mbedtls/(build_info|version)\.h$',
        r'MBEDTLS_VERSION_STRING\s+"([^"]+)"',
        GH + 'Mbed-TLS/mbedtls', 'mbedtls-{}'),
    'libgit2': (
        r'(^|/)git2/version\.h$',
        r'#define\s+LIBGIT2_VERSION\s+"([^"]+)"',
        GH + 'libgit2/libgit2', 'v{}'),
    'libyaml': (r'(^|/)yaml\.h$', None, GH + 'yaml/libyaml', '{}'),
    'miniz': (
        r'(^|/)miniz\.h$',
        r'#define\s+MZ_VERSION\s+"([^"]+)"',
        None, None),
}

# "plotly.js v2.11.1", "pym.js - v1.3.1", "jQuery v3.6.0"
JS_BANNER = r'([A-Za-z][\w.\-]*?(?:\.js)?)\s*(?:-\s*)?v(\d+\.\d+\.\d+)'
