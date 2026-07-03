# Conceptual architecture diagram (copy into slides)

Paste the block below into Mermaid Live Editor, Notion, GitHub, or slide tools that support Mermaid.

## Export as PNG or SVG (recommended)

1. Open [Mermaid Live Editor](https://mermaid.live).
2. Replace the default diagram with the contents of [`architecture-diagram.mmd`](architecture-diagram.mmd) (same graph as below).
3. Use **Actions → PNG** or **SVG** to download an image for PowerPoint, Keynote, Google Slides, or LaTeX Beamer.

## Local CLI (optional)

If you have Node.js and a working Chromium (or set `PUPPETEER_EXECUTABLE_PATH` to your Chrome binary):  
`npx @mermaid-js/mermaid-cli -i architecture-diagram.mmd -o architecture-diagram.png`

```mermaid
flowchart TB
  subgraph dataSources [Data sources]
    NHANES[NHANES structured labs and demographics]
    MIMIC[MIMIC-IV longitudinal ICU EHR]
    MIMICECG[MIMIC-IV-ECG 12-lead WFDB waveforms]
    WESAD[WESAD wearable multichannel signals]
  end

  subgraph ehrBranch [EHR branch with CKD labels]
    prepEHR[Harmonize features and time windows]
    modelEHR[Deep model CNN-RNN Transformer HERBERT-style]
    embEHR[EHR embedding z_ehr]
    NHANES --> prepEHR
    MIMIC --> prepEHR
    prepEHR --> modelEHR --> embEHR
  end

  subgraph ecgBranch [Clinical ECG branch paired with MIMIC]
    prepECG[12-lead segments WFDB resample normalize]
    modelECG[CNN or Transformer 1D ECG encoder]
    embECG[ECG embedding z_ecg]
    MIMICECG --> prepECG --> modelECG --> embECG
  end

  subgraph wearBranch [Wearable branch no CKD label]
    prepW[Preprocess segments windows]
    modelW[CNN LSTM or contrastive encoder]
    embW[Wearable embedding z_wear]
    WESAD --> prepW --> modelW --> embW
  end

  subgraph fusionLayer [Fusion]
    fuse[Concatenate attention gated fusion or small MLP]
    head[CKD early risk head no therapy]
    embEHR --> fuse
    embECG --> fuse
    embW --> fuse
    fuse --> head
  end

  subgraph xai [Explainability]
    shap[SHAP or LIME on EHR inputs]
    attn[Attention maps or Grad-CAM on waveforms]
    fuseExplain[Attribution on fusion weights optional]
    prepEHR -.-> shap
    prepECG -.-> attn
    prepW -.-> attn
    fuse -.-> fuseExplain
  end

  subgraph cds [Prototype CDS scope]
    viz[Risk SHAP charts signal maps]
  end

  head --> out[CKD stage or binary early risk]
  shap --> viz
  attn --> viz
  out --> viz
```
