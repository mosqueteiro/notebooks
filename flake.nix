{
  description = "Marimo Notebook Workspace";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        # dev tools and required system libraries here
        packages = [
          pkgs.uv
          pkgs.python314 # Nix-patched Python
          pkgs.stdenv.cc.cc.lib # Often needed for Python wheels that use C++
          pkgs.zlib # Common dependency for data science wheels
        ];

        shellHook = ''
          # Force uv to use the Nix-provided Python
          export UV_PYTHON_PREFERENCE="system"

          # Expose dynamically linked libraries to Python wheels
          export LD_LIBRARY_PATH="${
            pkgs.lib.makeLibraryPath [
              pkgs.stdenv.cc.cc.lib
              pkgs.zlib
            ]
          }:$LD_LIBRARY_PATH"

          echo "Ready to run 'uv run marimo edit'"
        '';
      };
    };
}
