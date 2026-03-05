{
  description = "Finwise MCP Server - Connect your Finwise personal finance data to LLMs";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
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
