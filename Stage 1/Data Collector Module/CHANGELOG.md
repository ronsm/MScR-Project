# Change Log
These are development libraries for Impinj RAIN RFID Readers (Speedway® R220 and 
R420) and Gateways (xPortal R640, xSpan R660 and xArray R680).

## [10.30.0.0]
#### Application Compatibility
| Library           | Version |
|-------------------|---------|
|Octane .NET SDK    | 2.30.0  |
|Octane Java SDK    | 1.30.0  |
|.NET LTK           | 10.30.0 |
|Java LTK           | 10.30.0 |
|C++ LTK for Win32  | 10.30.0 |
|C++ LTK for Linux  | 10.30.0 |
|C LTK for Linux    | 10.30.0 |
|LLRP Definitions   | 1.28    |
#### Firmware Compatibility
| Firmware        | Version |
|-----------------|---------|
| Octane Firmware | 5.12.0  |
#### Document Compatibility
| Document                                              | Version |
|-------------------------------------------------------|---------|
|Impinj Speedway Installation and Operations Manual     | 5.12.0  |
|Impinj xSpan/xArray Installation and Operations Manual | 5.12.0  |
|Impinj Firmware Upgrade Reference Manual               | 5.12.0  |
|Impinj RShell Reference Manual                         | 5.12.0  |
|Impinj Octane SNMP                                     | 5.12.0  |
|Impinj Octane LLRP                                     | 5.12.0  |
|Impinj LLRP Tool Kit (LTK) Programmers Guide           | 5.12.0  |
|Impinj Embedded Developers Guide                       | 5.12.0  |
### New Features
- Fixed an issue where Mina network handles may leak if you terminate your
  connection with a reader by sending the CLOSE_CONNECTION message prior to
  calling `LLRPConnector.disconnect()`.
- Updated samples to show the correct way to cleanly disconnect from a reader.

## [10.26.0] - 2016-12-19
#### Application Compatibility
| Library           | Version |
|-------------------|---------|
|Octane .NET SDK    | 2.26.0  |
|Octane Java SDK    | 1.26.0  |
|.NET LTK           | 10.26.0 |
|Java LTK           | 10.26.0 |
|C++ LTK for Win32  | 10.26.0 |
|C++ LTK for Linux  | 10.26.0 |
|C LTK for Linux    | 10.26.0 |
|LLRP Definitions   | 1.26.0  |
#### Firmware Compatibility
| Firmware        | Version |
|-----------------|---------|
| Octane Firmware | 5.10.0  |
#### Document Compatibility
| Document                                              | Version |
|-------------------------------------------------------|---------|
|Impinj Speedway Installation and Operations Manual     | 5.10.0  |
|Impinj xSpan/xArray Installation and Operations Manual | 5.10.0  |
|Impinj Firmware Upgrade Reference Manual               | 5.10.0  |
|Impinj RShell Reference Manual                         | 5.10.0  |
|Impinj Octane SNMP                                     | 5.10.0  |
|Impinj Octane LLRP                                     | 5.10.0  |
|Impinj LLRP Tool Kit (LTK) Programmers Guide           | 5.10.0  |
|Impinj Embedded Developers Guide                       | 5.10.0  |
### New Features
- Added IPv6 support to all libarries 
  - Octane .NET SDK 
  - Octane Java SDK 
  - .NET LTK 
  - Java LTK 
  - C++ LTK for Win32 
  - C++ LTK for Linux 
  - C LTK for Linux 
- Moved .NET LTK and .NET SDK to .NET Framework version 4.6.1 
- Removed xArrayLocationWam SDK example 

## [10.24.1] - 2016-10-26
#### Application Compatibility
| Library           | Version |
|-------------------|---------|
|Octane .NET SDK    | 2.24.1  |
|Octane Java SDK    | 1.24.1  |
|.NET LTK           | 10.24.1 |
|Java LTK           | 10.24.1 |
|C++ LTK for Win32  | 10.24.1 |
|C++ LTK for Linux  | 10.24.1 |
|C LTK for Linux    | 10.24.1 |
|LLRP Definitions   | 1.24.1  |
#### Firmware Compatibility
| Firmware        | Version |
|-----------------|---------|
| Octane Firmware |  5.8.1  |
#### Document Compatibility
| Document                                              | Version |
|-------------------------------------------------------|---------|
|Impinj Speedway Installation and Operations Manual     |  5.8.0  |
|Impinj xSpan/xArray Installation and Operations Manual |  5.8.0  |
|Impinj Firmware Upgrade Reference Manual               |  5.8.0  |
|Impinj RShell Reference Manual                         |  5.8.0  |
|Impinj Octane SNMP                                     |  5.8.0  |
|Impinj Octane LLRP                                     |  5.8.0  |
|Impinj LLRP Tool Kit (LTK) Programmers Guide           |  5.8.0  |
|Impinj Embedded Developers Guide                       |  5.8.0  |
### New Features
- New *SingleTargetReset* search mode.  Used in combination with *SingleTarget* 
  inventory to speed the completion of an inventory round by setting tags in B 
  state back to A state.
- New *SpatialConfig* class.  Used with xSpan and xArray gateways to configure 
  Direction Mode.  Used with the xArray gateway to configure Location Mode. 
- New *AntennaUtilities* class.  Used to provide an easier method of selecting 
  xSpan and xArray antenna beams by rings and sectors. 
- New *ImpinjMarginRead* class.  Used to check if Monza 6 tag IC memory cells 
  are fully charged, providing an additional measure of confidence in how well 
  the tag has been encoded.
### Changes
- All LTKs and SDKs now support connecting to readers over a secured connection. 
  Please see the library-specific documentation for more information on how to 
  make your application take advantage of this new feature. 
- All LTKs and SDKs now support Octane's new "Direction" feature for xArray.  
  Please see the library-specific documentation for more information on how to 
  use this new functionality. 
- The Java LTK has upgraded the version of Mina it uses to 2.0.9 (up from 1.1.7)
- For xArray-based applications using the SDK, transmit power can now be set 
  inside of the LocationConfig object. 
- All C and C++ LTKs now rely on the OpenSSL Libraries for network communication. 
  For the Win32 LTK, a copy of libeay32.dll and ssleay32.dll are provided.  For 
  the Linux C/C++ LTKs, libraries are only provided for the Atmel architecture 
  to enable linking for onreader apps.  Libraries for other architectures 
  running Linux are not provided as they should already be available from 
  your Linux distribution. 
- For the C, C++ for Linux, and C++ for Windows libraries, we implemented a fix 
  for non-blocking network communication for unencrypted (traditional) 
  connections to the reader.  However, if a user is attempting to connect over 
  a TLS-encrypted connection, non-blocking calls to recvMessage are still not 
  supported 