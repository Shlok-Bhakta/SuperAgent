{ pkgs ? import <nixpkgs> {} }:

let
  pythonPackages = ps: with ps; [
    # Core scientific packages
    numpy
    pandas
    scipy
    scikit-learn
    matplotlib
    seaborn
    plotly
    ipython
    jupyter
    notebook
    
    # Deep learning frameworks
    # torch
    # torchvision
    # torchaudio
    # tensorflow
    # tensorflowWithCuda
    # pytorchWithCuda
    baselines
    # keras

    
    # Image processing
    pillow
    opencv4
    
    # Data manipulation
    pyarrow
    fastparquet
    sqlalchemy
    
    # Machine learning
    xgboost 
    lightgbm
    catboost
    statsmodels
    flask
    
    # NLP packages
    # nltk
    # spacy
    # transformers
    
    # Utilities
    tqdm
    requests
    beautifulsoup4
    virtualenv
    
    # Development tools
    ipykernel
    black
    mypy
    pylint
    pytest
  ];
in
pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    # Existing tools
    libgcc
    gdb
    lldb_18
    llvm_18
    diffutils
    clang-tools
    gcc-unwrapped
    
    # Additional system packages from Colab
    git
    wget
    curl
    ffmpeg
    imagemagick
    pandoc
    
    
    # Python with all packages
    (python311.withPackages pythonPackages)
    
    # Development tools
    cmake
    gnumake
    pkg-config
    
    # Node.js for Jupyter extensions
    nodejs
    
    # Additional utilities
    htop
    tmux
    jq
  ];

  # Environment variables for CUDA
  shellHook = ''
    
    # Start zsh as the interactive shell
    zsh
  '';
}