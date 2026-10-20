"""Lazy EDF/FIF (MNE) and NWB (PyNWB) readers, opt-in with separate data rights."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np

from .contracts import Channel, Chunk, Event, Recording, Rights


class SignalReader(Protocol):
    metadata: Recording

    def read(self, start: int, stop: int) -> Chunk: ...
    def close(self) -> None: ...


def _approved_path(path: Path, root: Path, ext: tuple[str, ...], rights: Rights) -> Path:
    candidate = path.resolve(strict=True)
    if not candidate.is_file() or not candidate.is_relative_to(root.resolve(strict=True)):
        raise ValueError("source must be a file under the approved data root")
    if candidate.suffix.lower() not in ext:
        raise ValueError("unsupported format")
    if rights.is_synthetic or not (rights.permission_verified and rights.allow_analysis):
        raise ValueError("external source rights not verified")
    # Caller must furnish a trustworthy checksum, validated by bytes streaming.
    from hashlib import sha256
    digest = sha256()
    with candidate.open("rb") as fp:
        for block in iter(lambda: fp.read(1 << 20), b""):
            digest.update(block)
    if digest.hexdigest() != rights.content_sha256:
        raise ValueError("source checksum mismatch")
    return candidate


class MNEReader:
    """EDF/FIF: channel x time in SI volts for EEG, EOG and ECG (non-EEG rejected)."""

    def __init__(self, path: Path, root: Path, rights: Rights, recording_id: str):
        path = _approved_path(path, root, (".edf", ".fif"), rights)
        try:
            import mne
        except ImportError as exc:
            raise RuntimeError("Install extra '[eeg]' for MNE readers") from exc
        self._raw = (mne.io.read_raw_edf(path, preload=False, verbose="ERROR")
                     if path.suffix.lower() == ".edf" else
                     mne.io.read_raw_fif(path, preload=False, verbose="ERROR"))
        kinds = self._raw.get_channel_types()
        if not kinds or any(k not in {"eeg", "eog", "ecg"} for k in kinds):
            self._raw.close()
            raise ValueError("only EEG/EOG/ECG voltage channels supported; select types upstream")
        sfreq = float(self._raw.info["sfreq"])
        events = []
        for onset, duration, description in zip(
            self._raw.annotations.onset, self._raw.annotations.duration,
            self._raw.annotations.description, strict=True
        ):
            # Index in raw-relative sample space; annotation onset may include first_samp offset.
            index = int(self._raw.time_as_index([onset - self._raw.first_time], use_rounding=True)[0])
            if 0 <= index < self._raw.n_times:
                events.append(Event(sample=index, code=str(description)[:64],
                                    duration_samples=min(max(round(duration * sfreq), 0),
                                                         self._raw.n_times - index)))
        self.metadata = Recording(
            recording_id=recording_id, sample_rate_hz=sfreq, samples=self._raw.n_times,
            channels=tuple(Channel(name=name, kind=kind, bad=name in self._raw.info["bads"])
                           for name, kind in zip(self._raw.ch_names, kinds, strict=True)),
            events=tuple(events), rights=rights)

    def read(self, start: int, stop: int) -> Chunk:
        if not (0 <= start < stop <= self.metadata.samples):
            raise ValueError("invalid slice")
        volts = self._raw.get_data(start=start, stop=stop, reject_by_annotation=None)
        return Chunk(recording_id=self.metadata.recording_id, start=start,
                     sample_rate_hz=self.metadata.sample_rate_hz,
                     channel_names=tuple(c.name for c in self.metadata.channels),
                     volts=volts.tolist())

    def close(self) -> None:
        self._raw.close()

    def __enter__(self) -> MNEReader:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


class NWBReader:
    """PyNWB ecephys ElectricalSeries with uniform sampling; HDF5 handle stays open."""

    def __init__(self, path: Path, root: Path, rights: Rights, recording_id: str,
                 series_name: str = "ElectricalSeries"):
        path = _approved_path(path, root, (".nwb",), rights)
        try:
            from pynwb import NWBHDF5IO
        except ImportError as exc:
            raise RuntimeError("Install extra '[nwb]' for NWB readers") from exc
        self._io = NWBHDF5IO(str(path), mode="r", load_namespaces=False)
        try:
            nwb = self._io.read()
            series = nwb.acquisition[series_name]
            if series.neurodata_type != "ElectricalSeries":
                raise ValueError("series is not ElectricalSeries")
            if series.timestamps is not None or not series.rate or series.rate <= 0:
                raise ValueError("nonuniform NWB timestamps require explicit resampling contract")
            if str(series.unit).lower() not in {"volts", "volt", "v"}:
                raise ValueError("NWB electrical series unit is not volts")
            shape = series.data.shape  # time x electrodes, no eager read
            if len(shape) != 2 or shape[1] < 1:
                raise ValueError("NWB ElectricalSeries must be two-dimensional")
            self._series = series
            electrode_rows = list(series.electrodes.data[:])
            if len(electrode_rows) != shape[1]:
                raise ValueError("electrode/channel count mismatch")
            # Reference DynamicTableRegion via get to preserve electrode ordering.
            table = series.electrodes.table
            labels = [str(table["label"][int(i)]) if "label" in table.colnames
                      else f"electrode_{int(i)}" for i in electrode_rows]
            self.metadata = Recording(
                recording_id=recording_id, sample_rate_hz=float(series.rate),
                samples=int(shape[0]),
                channels=tuple(Channel(name=name) for name in labels), rights=rights)
        except Exception:
            self._io.close()
            raise

    def read(self, start: int, stop: int) -> Chunk:
        if not (0 <= start < stop <= self.metadata.samples):
            raise ValueError("invalid slice")
        series = self._series
        # NWB convention: stored values * conversion + offset, in declared unit (V).
        samples = np.asarray(series.data[start:stop, :], dtype=np.float64)
        volts = (samples * float(series.conversion) + float(series.offset)).T
        return Chunk(recording_id=self.metadata.recording_id, start=start,
                     sample_rate_hz=self.metadata.sample_rate_hz,
                     channel_names=tuple(c.name for c in self.metadata.channels),
                     volts=volts.tolist())

    def close(self) -> None:
        self._io.close()

    def __enter__(self) -> NWBReader:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
