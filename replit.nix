{pkgs}: {
  deps = [
    pkgs.zip
    pkgs.awscli
    pkgs.unzip
    pkgs.aws-sam-cli
    pkgs.ffmpeg-full
    pkgs.postgresql
    pkgs.openssl
  ];
}
