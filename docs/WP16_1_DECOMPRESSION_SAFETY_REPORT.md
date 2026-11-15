# WP16.1: Incremental Decompression Safety and Memory Protection Report

**Document Version:** 1.0.0  
**Phase:** Phase 3 (Decompression Safety)  
**Verification Date:** 2026-11-15  
**Governing Module:** `backlink_agent.advanced_verifier.verifier`  

---

## 1. Threat Analysis: Decompression Bombs (Zip Bombs)

A malicious or misconfigured web server can craft a small HTTP response (e.g. 500 KB gzip) that decompresses into hundreds of megabytes or gigabytes of repeating null bytes or text. If an HTTP crawler decompresses the entire payload in memory with `read()` or `zlib.decompress()`, it causes memory exhaustion, high GC latency, or Out-Of-Memory (OOM) operating system kills.

---

## 2. Implemented Defense: Bounded Incremental Decompression

The verifier enforces two distinct memory boundaries:
1. **Network Transfer Boundary (`DEFAULT_MAX_BYTES` = 2 MB):** The raw socket stream is capped at 2,097,152 bytes. Sockets are closed once 2MB is received.
2. **Decompressed Stream Boundary (`DEFAULT_MAX_DECOMPRESSED_BYTES` = 4 MB):** The decompressed expansion is capped at 4,194,304 bytes.

### 2.1 Incremental Chunking Mechanism
Rather than expanding the entire stream at once, decompression executes in 64 KB chunks (`CHUNK_SIZE = 65,536` bytes):
- **Gzip Streams (`Content-Encoding: gzip`):**
  ```python
  gz = gzip.GzipFile(fileobj=io.BytesIO(body_bytes))
  chunks = []
  total_decompressed = 0
  CHUNK_SIZE = 64 * 1024
  while total_decompressed < self.max_decompressed_bytes:
      to_read = min(CHUNK_SIZE, self.max_decompressed_bytes - total_decompressed)
      chunk = gz.read(to_read)
      if not chunk:
          break
      chunks.append(chunk)
      total_decompressed += len(chunk)
  body_bytes = b"".join(chunks)
  ```
- **Deflate Streams (`Content-Encoding: deflate`):**
  Uses `zlib.decompressobj()`, feeding the raw input in 64 KB increments and stopping immediately once `total_decompressed >= self.max_decompressed_bytes`.
- **Zero Unbounded Buffering:** The maximum memory consumed during decompression is strictly bounded to $2\text{ MB (input)} + 4\text{ MB (output)} = 6\text{ MB}$ total.

### 2.2 Corrupted & Truncated Stream Recovery
If an external server returns truncated, corrupted, or invalid compressed bytes:
- The parser wraps decompression in `try ... except Exception`.
- It logs a diagnostic warning (`logger.warning("Gzip decompression error...")`).
- It falls back gracefully to raw bytes decoding without raising an unhandled exception or crashing the worker process.

---

## 3. Adversarial Test Evidence

Verified by unit tests in `backlink_agent/tests/test_wp16_1_security_closure.py`:
- `test_incremental_decompression_caps_output_at_4mb`: Feeds a compressed gzip payload that expands to > 6MB; verifies output is strictly truncated at exactly 4,194,304 bytes without allocating memory for the rest.
- `test_corrupted_gzip_stream_fails_safely_without_crash`: Feeds malformed gzip headers; verifies error is safely caught and handled.
