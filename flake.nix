{
  description = "Ambiente Python + pygame";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };
  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux"; # or aarch64-linux, etc.
      pkgs = import nixpkgs { inherit system; };
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [
        pygame-ce
        pygame-gui
        pip
        virtualenv
      ]);
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pythonEnv
          pkgs.SDL2
          pkgs.SDL2_image
          pkgs.SDL2_mixer
          pkgs.SDL2_ttf
          pkgs.alsa-lib
          pkgs.pulseaudio
          pkgs.xorg.libX11
          pkgs.vulkan-loader
        ];
        LD_LIBRARY_PATH = "${pkgs.vulkan-loader}/lib";
        shellHook = ''
          echo "Python + Pygame pronto 🚀"
          python --version
        '';
      };
    };
}