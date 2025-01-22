from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HistogramSample(_message.Message):
    __slots__ = ["bucket_ends", "counts"]
    BUCKET_ENDS_FIELD_NUMBER: _ClassVar[int]
    COUNTS_FIELD_NUMBER: _ClassVar[int]
    bucket_ends: _containers.RepeatedScalarFieldContainer[float]
    counts: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, bucket_ends: _Optional[_Iterable[float]] = ..., counts: _Optional[_Iterable[float]] = ...) -> None: ...

class MetricData(_message.Message):
    __slots__ = ["histogram_sample", "labels", "metric_sample", "name"]
    class LabelsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    HISTOGRAM_SAMPLE_FIELD_NUMBER: _ClassVar[int]
    LABELS_FIELD_NUMBER: _ClassVar[int]
    METRIC_SAMPLE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    histogram_sample: HistogramSample
    labels: _containers.ScalarMap[str, str]
    metric_sample: MetricSample
    name: str
    def __init__(self, name: _Optional[str] = ..., labels: _Optional[_Mapping[str, str]] = ..., metric_sample: _Optional[_Union[MetricSample, _Mapping]] = ..., histogram_sample: _Optional[_Union[HistogramSample, _Mapping]] = ...) -> None: ...

class MetricSample(_message.Message):
    __slots__ = ["times", "values"]
    TIMES_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    times: _containers.RepeatedScalarFieldContainer[int]
    values: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, times: _Optional[_Iterable[int]] = ..., values: _Optional[_Iterable[float]] = ...) -> None: ...

class RangeQueryRequest(_message.Message):
    __slots__ = ["query", "relative", "start", "step", "stop"]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    query: str
    relative: str
    start: str
    step: str
    stop: str
    def __init__(self, query: _Optional[str] = ..., relative: _Optional[str] = ..., start: _Optional[str] = ..., stop: _Optional[str] = ..., step: _Optional[str] = ...) -> None: ...

class RangeQueryResponse(_message.Message):
    __slots__ = ["results"]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[MetricData]
    def __init__(self, results: _Optional[_Iterable[_Union[MetricData, _Mapping]]] = ...) -> None: ...
