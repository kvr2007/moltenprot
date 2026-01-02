"MoltenProt unit tests"

import subprocess
from unittest import TestCase, main
from tempfile import TemporaryDirectory
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from moltenprot import core

DEMO_DATA_PATH = Path(core.__location__) / "demo_data"
# readouts that should be present in XLSX data
EXPECTED_READOUTS = ("Ratio", "330nm", "350nm", "Scattering", "deltaF")
# fit values to compare between the reference computation and current
COMPARISON_METRICS = ("S", "Tm_fit", "dG_std")


class TestPrototype(TestCase):
    "Provides shared methods for different tests"

    def _read_reference(self) -> core.MoltenProtFitMultiple:
        "Reads reference MoltenProt output"
        return core.mp_from_json(DEMO_DATA_PATH / "Ratio_F330_F350_Scattering48.json")


class TestFileReaders(TestPrototype):
    "Check if demo files are read without errors"

    def test_spectrum_csv(self):
        "reading a CSV file with a spectrum"
        infile = DEMO_DATA_PATH / "FL_spectrum.csv"
        data = core.parse_spectrum_csv(infile).datasets
        self.assertEqual(len(data), 1)
        self.assertTrue("Signal" in data)

    def test_prom_xlsx(self):
        "reading exported XLSX file"
        infile = DEMO_DATA_PATH / "Ratio_F330_F350_Scattering48.xlsx"
        data = core.parse_prom_xlsx(infile).datasets
        self.assertEqual(len(data), 5)
        for readout_name in EXPECTED_READOUTS:
            self.assertTrue(readout_name in data)

    def test_plain_csv(self):
        "reading CSV with Temperature vs A1-H12"
        infile = DEMO_DATA_PATH / "Ratio96.csv"
        data = core.parse_plain_csv(infile).datasets
        self.assertEqual(len(data), 1)
        self.assertTrue("Signal" in data)

    def test_mp_json(self):
        "reading internal format"
        data = self._read_reference().datasets
        self.assertEqual(len(data), 5)
        for readout_name in EXPECTED_READOUTS:
            self.assertTrue(readout_name in data)


class TestDataAnalysis(TestPrototype):
    "Check if fit results are consistent with prior version"

    def _read_target(
        self, ratio_only: bool = False, le: bool = False
    ) -> core.MoltenProtFitMultiple:
        "Reads test MoltenProt data"
        mp = core.parse_prom_xlsx(
            DEMO_DATA_PATH / "Ratio_F330_F350_Scattering48.xlsx", LE=le
        )
        # remove extra readouts
        if ratio_only:
            for dset_name in list(mp.datasets.keys()):
                if not "ratio" in dset_name.lower():
                    mp.DelDataset(dset_name)
        return mp

    def test_reference(self):
        "Compare settings between the reference set and fresh processing"
        reference = self._read_reference()
        target = self._read_target()
        # extract analysis settings from reference and apply to the target
        for dset_type, dset in reference.datasets.items():
            settings = {}
            for setting in (
                "model",
                "baseline_fit",
                "baseline_bounds",
                "savgol",
                "blanks",
                "exclude",
                "invert",
                "mfilt",
                "shrink",
                "trim_min",
                "trim_max",
            ):
                settings[setting] = getattr(dset, setting)
                target.datasets[dset_type].SetAnalysisOptions(**settings)
        # run analysis
        target.PrepareAndAnalyseAll()
        # compare outputs with the the reference
        for dset_type, ref_dset in reference.datasets.items():
            if ref_dset.model == "skip":
                continue
            targ_dset = target.datasets.get(dset_type)
            self.assertTrue(targ_dset is not None)
            ref_result = ref_dset.plate_results
            targ_result = targ_dset.plate_results
            for metric in COMPARISON_METRICS:
                if metric not in ref_result.columns:
                    continue
                side_by_side = pd.concat(
                    [ref_result[metric], targ_result[metric]], axis=1
                ).dropna(how="any", axis=0)
                # in newer versions poor fits have np.inf, this crashes the comparisons
                side_by_side = side_by_side.loc[~np.isinf(side_by_side.iloc[:, 1]), :]
                # NOTE we check pearson correlation, but can also consider max error
                corr = pearsonr(
                    side_by_side.iloc[:, 0], side_by_side.iloc[:, 1]
                ).statistic
                print(
                    f"### {dset_type} {metric} corr {corr:0.3f}",
                )
                self.assertTrue(corr >= 0.98)

    def _run_analysis(self, model=None, exclude=None, n_jobs=1, ratio_only=False):
        "Helper function to run analyses"
        if model is None:
            model = core.analysis_defaults["model"]
        if exclude is None:
            exclude = core.prep_defaults["exclude"]
        mp = self._read_target(ratio_only=ratio_only, le=model == "lumry_eyring")
        mp.SetAnalysisOptions(model=model, exclude=exclude)
        mp.PrepareAndAnalyseAll(n_jobs=n_jobs)

    def test_defaults(self):
        "Process the data with current defaults"
        self._run_analysis()

    def test_defaults_parallel(self):
        "Run multiprocess analysis with current defaults"
        if core.parallelization:
            self._run_analysis(n_jobs=4)

    def test_irrev(self):
        "Test irrversible model with sample A1 using Ratio data"
        self._run_analysis(
            model="irrev", exclude=list(core.alphanumeric_index[1:]), ratio_only=True
        )

    def test_lumry_eyring(self):
        "Test Lumry-Eyring model with sample A1"
        self._run_analysis(
            model="lumry_eyring", exclude=list(core.alphanumeric_index[1:])
        )


class TestReport(TestPrototype):
    "Report tests - using precomputed result"

    def test_html_report(self, n_jobs=1):
        "test output in HTML format"
        mp = self._read_reference()
        with TemporaryDirectory() as outfolder:
            mp.WriteOutputAll(
                outfolder=outfolder, report_format="html", session=False, n_jobs=n_jobs
            )

    def test_html_report_parallel(self):
        "test output in HTML format with code parallelization"
        if core.parallelization:
            self.test_html_report(n_jobs=4)

    def test_pdf_report(self):
        "test output in PDF format"
        mp = self._read_reference()
        with TemporaryDirectory() as outfolder:
            mp.WriteOutputAll(outfolder=outfolder, report_format="pdf", session=False)

    def test_xlsx_report(self):
        "test output in XLSX format"
        mp = self._read_reference()
        with TemporaryDirectory() as outfolder:
            mp.WriteOutputAll(outfolder=outfolder, report_format="xlsx", session=False)


class TestCli(TestPrototype):
    "Tests for the command-line interface"

    def test_cli_default(self):
        "Basic run of the command line"
        with TemporaryDirectory() as outfolder:
            subprocess.run(
                [
                    "moltenprot",
                    "-i",
                    str(DEMO_DATA_PATH / "Ratio_F330_F350_Scattering48.xlsx"),
                    "-o",
                    outfolder,
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
