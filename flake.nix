{
  description = "Finwise MCP Server - Connect your Finwise personal finance data to LLMs";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, pyproject-nix, uv2nix, pyproject-build-systems }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

        overlay = workspace.mkPyprojectOverlay {
          sourcePreference = "wheel";
        };

        python = pkgs.python312;

        pythonSet =
          (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope
            (
              pkgs.lib.composeManyExtensions [
                pyproject-build-systems.overlays.default
                overlay
              ]
            );

        venv = pythonSet.mkVirtualEnv "finwise-mcp-env" workspace.deps.default;

      in
      {
        packages.default = venv;

        apps.default = {
          type = "app";
          program = "${venv}/bin/finwise-mcp";
        };

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python312
            uv
          ];

          shellHook = ''
            echo ""
            echo "Finwise MCP Server"
            echo "=================="
            echo ""
            echo "Setup:"
            echo "  uv sync                      Install Python dependencies"
            echo ""
            echo "Development:"
            echo "  uv run mcp dev src/finwise_mcp/server.py"
            echo "                               Launch MCP Inspector for testing"
            echo ""
            echo "Note: Set FINWISE_API_KEY in .env or export it directly"
            echo ""
          '';
        };
      }
    );
}
