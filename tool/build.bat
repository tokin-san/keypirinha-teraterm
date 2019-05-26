@echo off

set PACKAGE_NAME=TeraTerm
set SOURCE_DIR=..\src
set BUILD_DIR=..\build

if exist "%BUILD_DIR%" rmdir /q /s "%BUILD_DIR%"
mkdir "%BUILD_DIR%"

pushd "%SOURCE_DIR%"
powershell compress-archive .\* "%BUILD_DIR%\%PACKAGE_NAME%.zip"
rename "%BUILD_DIR%\%PACKAGE_NAME%.zip" "%PACKAGE_NAME%.keypirinha-package"
popd
