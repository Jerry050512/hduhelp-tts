# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: proto/audio.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'proto/audio.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11proto/audio.proto\x12\x05proto\")\n\x13\x41\x64\x64UserVoiceRequest\x12\x12\n\naudio_list\x18\x01 \x03(\t\".\n\x14\x41\x64\x64UserVoiceResponse\x12\x16\n\x0evoice_filename\x18\x01 \x01(\t\"\xa1\x01\n\nTTSRequest\x12\x0c\n\x04text\x18\x01 \x01(\t\x12\x10\n\x08language\x18\x02 \x01(\t\x12\x0e\n\x06\x65ngine\x18\x03 \x01(\t\x12\x17\n\nspeaker_id\x18\x04 \x01(\x05H\x00\x88\x01\x01\x12\r\n\x05speed\x18\x05 \x01(\x02\x12\x1a\n\rrefine_prompt\x18\x06 \x01(\tH\x01\x88\x01\x01\x42\r\n\x0b_speaker_idB\x10\n\x0e_refine_prompt\"%\n\x0bTTSResponse\x12\x16\n\x0e\x61udio_filename\x18\x01 \x01(\t\"P\n\x16VoiceConversionRequest\x12\x1a\n\x12src_audio_filename\x18\x01 \x01(\t\x12\x1a\n\x12ref_voice_filename\x18\x02 \x01(\t\";\n\x17VoiceConversionResponse\x12 \n\x18\x63onverted_audio_filename\x18\x01 \x01(\t\"$\n\nASRRequest\x12\x16\n\x0e\x61udio_filename\x18\x01 \x01(\t\"#\n\x0b\x41SRResponse\x12\x14\n\x0csrt_filename\x18\x01 \x01(\t2\x85\x02\n\x0c\x41udioService\x12G\n\x0c\x41\x64\x64UserVoice\x12\x1a.proto.AddUserVoiceRequest\x1a\x1b.proto.AddUserVoiceResponse\x12,\n\x03TTS\x12\x11.proto.TTSRequest\x1a\x12.proto.TTSResponse\x12P\n\x0fVoiceConversion\x12\x1d.proto.VoiceConversionRequest\x1a\x1e.proto.VoiceConversionResponse\x12,\n\x03\x41SR\x12\x11.proto.ASRRequest\x1a\x12.proto.ASRResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.audio_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ADDUSERVOICEREQUEST']._serialized_start=28
  _globals['_ADDUSERVOICEREQUEST']._serialized_end=69
  _globals['_ADDUSERVOICERESPONSE']._serialized_start=71
  _globals['_ADDUSERVOICERESPONSE']._serialized_end=117
  _globals['_TTSREQUEST']._serialized_start=120
  _globals['_TTSREQUEST']._serialized_end=281
  _globals['_TTSRESPONSE']._serialized_start=283
  _globals['_TTSRESPONSE']._serialized_end=320
  _globals['_VOICECONVERSIONREQUEST']._serialized_start=322
  _globals['_VOICECONVERSIONREQUEST']._serialized_end=402
  _globals['_VOICECONVERSIONRESPONSE']._serialized_start=404
  _globals['_VOICECONVERSIONRESPONSE']._serialized_end=463
  _globals['_ASRREQUEST']._serialized_start=465
  _globals['_ASRREQUEST']._serialized_end=501
  _globals['_ASRRESPONSE']._serialized_start=503
  _globals['_ASRRESPONSE']._serialized_end=538
  _globals['_AUDIOSERVICE']._serialized_start=541
  _globals['_AUDIOSERVICE']._serialized_end=802
# @@protoc_insertion_point(module_scope)
