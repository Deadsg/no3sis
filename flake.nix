{
  description = "A lattice of flakes for the Synapse system.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";

    pip2nix = {
      url = "github:meta-introspector/pip2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };

    # Agents
    base-agent = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/base-agent"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    architect = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/architect"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    clarity-judge = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/clarity-judge"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    code-hound = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/code-hound"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    devops-engineer = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/devops-engineer"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    docs-writer = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/docs-writer"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    file-creator = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/file-creator"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    git-workflow = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/git-workflow"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    golang-specialist = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/golang-specialist"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    python-specialist = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/python-specialist"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    rust-specialist = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/rust-specialist"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    security-specialist = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/security-specialist"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    boss = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/boss"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    test-runner = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/test-runner"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    tool-runner = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/tool-runner"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    typescript-specialist = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/typescript-specialist"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    ux-designer = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/ux-designer"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
    pneuma = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/pneuma"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; inputs.base-agent.follows = "base-agent"; };

    # Mojo
    mojo-runtime = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/mojo-runtime"; inputs.nixpkgs.follows = "nixpkgs"; };
    mojo-pattern-search = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/mojo-pattern-search"; inputs.nixpkgs.follows = "nixpkgs"; inputs.mojo-runtime.follows = "mojo-runtime"; };
    mojo-message-router = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/mojo-message-router"; inputs.nixpkgs.follows = "nixpkgs"; inputs.mojo-runtime.follows = "mojo-runtime"; };

    # Formal verification
    lean4-verification = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/lean4-verification"; inputs.nixpkgs.follows = "nixpkgs"; };
    synapse-core = { url = "github:no3sis-lattice/synapse?dir=nix/flakes/synapse-core"; inputs.nixpkgs.follows = "nixpkgs"; };
    duality = { url = "github:no3sis-lattice/synapse?dir=docs/duality"; inputs.nixpkgs.follows = "nixpkgs"; inputs.flake-utils.follows = "flake-utils"; };
  };

  outputs = { self, nixpkgs, flake-utils, pip2nix, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        # FIXED: pythonBase import matches expected arguments
        pythonBase = import ./nix/modules/python-base.nix {
          pkgs = pkgs;
          stdenv = pkgs.stdenv;
          python = pkgs.python3;
          overrides = {};
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [ redis ]);

        # Guarded pip2nix
        pip2nixPackages = if builtins.hasAttr "packages" pip2nix then pip2nix.packages.${system} else {};
        pip2nixPkg = if builtins.hasAttr "pip2nix" pip2nixPackages then pip2nixPackages.pip2nix
                     else if builtins.hasAttr "pip2nix_python39" pip2nixPackages then pip2nixPackages.pip2nix_python39
                     else null;

        # Optional no3sis-core
        no3sisCorePkg = if builtins.hasAttr "no3sis-core" inputs
                        && builtins.hasAttr "${system}" inputs.no3sis-core.packages
                        then inputs.no3sis-core.packages.${system}.no3sis-core
                        else null;

      in {
        packages = {
          default = pkgs.writeShellScriptBin "no3sis-system" ''
            echo "Synapse System - Multi-agent development platform"
            echo "Available agents: boss, architect, code-hound, etc."
            echo "Use 'synapse --help' for CLI commands"
          '';

          inherit (inputs.architect.packages.${system}) architect;
          inherit (inputs.clarity-judge.packages.${system}) clarity-judge;
          inherit (inputs.code-hound.packages.${system}) code-hound;
          inherit (inputs.devops-engineer.packages.${system}) devops-engineer;
          inherit (inputs.docs-writer.packages.${system}) docs-writer;
          inherit (inputs.file-creator.packages.${system}) file-creator;
          inherit (inputs.git-workflow.packages.${system}) git-workflow;
          inherit (inputs.golang-specialist.packages.${system}) golang-specialist;
          inherit (inputs.python-specialist.packages.${system}) python-specialist;
          inherit (inputs.rust-specialist.packages.${system}) rust-specialist;
          inherit (inputs.security-specialist.packages.${system}) security-specialist;
          inherit (inputs.boss.packages.${system}) boss;
          inherit (inputs.test-runner.packages.${system}) test-runner;
          inherit (inputs.tool-runner.packages.${system}) tool-runner;
          inherit (inputs.typescript-specialist.packages.${system}) typescript-specialist;
          inherit (inputs.ux-designer.packages.${system}) ux-designer;
          inherit (inputs.pneuma.packages.${system}) Pneuma;

          mojo-runtime = inputs.mojo-runtime.packages.${system}.mojo;
          inherit (inputs.mojo-pattern-search.packages.${system}) libpattern_search;
          inherit (inputs.mojo-message-router.packages.${system}) libmessage_router;

          lean4-verification = inputs.lean4-verification.packages.${system}.lean4-verification;
          lean4-verification-test = inputs.lean4-verification.packages.${system}.lean4-verification-test;
          lean4-verification-docs = inputs.lean4-verification.packages.${system}.lean4-verification-docs;
          lean = inputs.lean4-verification.packages.${system}.lean;

          mojo-libraries = pkgs.buildEnv {
            name = "synapse-mojo-libraries";
            paths = [
              inputs.mojo-pattern-search.packages.${system}.libpattern_search
              inputs.mojo-message-router.packages.${system}.libmessage_router
            ];
          };

          synapse-core = no3sisCorePkg;
          synapse-cli = if no3sisCorePkg != null then no3sisCorePkg else null;

          python-base = pythonBase.env;
        };

        devShells = {
          default = pkgs.mkShell {
            buildInputs = [
              pythonEnv
              (if pip2nixPkg != null then pip2nixPkg else pkgs.stdenv.cc)
              inputs.mojo-runtime.packages.${system}.default
              inputs.lean4-verification.packages.${system}.lean
            ];

            shellHook = ''
              echo "🧠 Synapse Development Environment"
              echo "Python: $(python --version)"
              echo "Mojo: $(mojo --version 2>&1 | head -n1 || echo 'Not available')"
              echo "Lean4: $(lean --version 2>&1 | head -n1 || echo 'Not available')"
            '';
          };

          mojo-dev = pkgs.mkShell {
            buildInputs = with pkgs; [
              inputs.mojo-runtime.packages.${system}.default
              python3
              python3Packages.ctypes
              gnumake
              binutils
              git
            ];

            shellHook = ''
              echo "🔥 Mojo Development Environment for Synapse"
              echo "Mojo version: $(mojo --version 2>&1 | head -n1)"
            '';
          };

          lean4-dev = inputs.lean4-verification.devShells.${system}.default;
          duality = inputs.duality.devShells.${system}.default;
        };
      }
    );
}
