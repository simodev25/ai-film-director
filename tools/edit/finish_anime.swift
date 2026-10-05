// finish_anime.swift — LOCAL, FREE image finishing for an ordered list of clips (hard cuts).
// Repository tool generalised from projects/la-pomme/production/scene-01/finish_anime.swift:
// identical rendering; project paths and provenance metadata are parameters.
//
// No model, no network, no generation, no paid call. AVFoundation + CoreImage only (no ffmpeg).
// Per clip: "animation on twos" (24 fps output, each sampled source image held 2 frames, no
// interpolation) → shared night grade → discreet highlight bloom → vignette → seeded animated
// film grain. Clips are concatenated with hard cuts; the audio bed is a wav laid at 0 s and
// trimmed to the picture. Optional 2.39 letterbox writes a SECOND output from the same frames.
//
// Build:  swiftc -O -o /tmp/finish_anime tools/edit/finish_anime.swift
// Run:    finish_anime --out final/scene-01/scene01-finished-v2.mp4
//                      [--audio audio/opening-rain/rain-preview.wav] [--letterbox 2.39]
//                      [--project-root DIR] [--seed 20261005] [--report R.json] [--contact C.png]
//                      [--tier T] [--video-model ID] [--model-folder F]
//                      [--clips-file list.txt]  clip1.mp4 ... clipN.mp4
// Relative paths (outputs, audio, clips, clips-file entries) resolve against --project-root
// (default: current directory). --tier/--video-model/--model-folder are recorded verbatim in the
// report provenance; when omitted they are recorded as null (unknown), never guessed.
// Outputs (refuses to overwrite any): <out>, <out stem>-letterbox.mp4 (if --letterbox),
//                                      <out stem>.report.json, <out stem>-contact.png
// Exit codes: 0 ok, 2 bad inputs (nothing written), 3 render/validation failure (partials removed), 64 usage.

import Foundation
import AVFoundation
import CoreImage
import CoreImage.CIFilterBuiltins
import CoreText
import ImageIO
import UniformTypeIdentifiers
import CryptoKit

// MARK: - Fixed finishing parameters (identical for every clip)

let EXPOSURE_EV: CGFloat = -0.10, SATURATION: CGFloat = 0.80, CONTRAST: CGFloat = 1.04
let CURVE: [CGPoint] = [CGPoint(x: 0, y: 0), CGPoint(x: 0.12, y: 0.06), CGPoint(x: 0.45, y: 0.40),
                        CGPoint(x: 0.80, y: 0.76), CGPoint(x: 1.0, y: 0.93)]
let TINT_GAIN: [CGFloat] = [0.92, 0.99, 1.05], TINT_BIAS: [CGFloat] = [0.0, 0.006, 0.014]
let BLOOM_THRESHOLD: CGFloat = 0.55, BLOOM_GAIN: CGFloat = 2.2, BLOOM_RADIUS: CGFloat = 16, BLOOM_MIX: CGFloat = 0.16
let VIG_INNER: CGFloat = 0.45, VIG_OUTER: CGFloat = 1.0, VIG_EDGE_GAIN: CGFloat = 0.84   // radii as fraction of centre-to-corner distance
let GRAIN_AMP: CGFloat = 0.12, GRAIN_SCALE: CGFloat = 1.4, GRAIN_SOFTEN: CGFloat = 0.6

let P: [String: Any] = [
    "output": ["width": 1280, "height": 720, "fps": 24, "codec": "h264_high", "video_bitrate": 10_000_000,
               "audio": "aac_48k_stereo_192k"],
    "animation_on_twos": ["hold_frames": 2, "effective_images_per_second": 12,
                          "method": "sample source image at time floor(i/2)*2/24 of clip-local output frame i; nearest earlier source frame; no interpolation; hold resets at every cut"],
    "grade_night": ["order": "bloom(linear, additive) -> exposure(linear) -> [sRGB-encoded: saturation/contrast -> tone curve -> night tint -> vignette -> grain] -> linear",
                    "exposure_ev": EXPOSURE_EV, "saturation": SATURATION, "contrast": CONTRAST,
                    "tone_curve_srgb": CURVE.map { [$0.x, $0.y] }, "tint_rgb_gain": TINT_GAIN, "tint_rgb_bias": TINT_BIAS,
                    "intent": "deeper blacks, light desaturation, green/blue night cast, soft highlight roll-off (white -> 0.93)"],
    "bloom": ["threshold_linear": BLOOM_THRESHOLD, "gain": BLOOM_GAIN, "blur_radius_px": BLOOM_RADIUS, "mix": BLOOM_MIX,
              "note": "per-channel highlights only (TV, window), blurred, additive, pre-grade"],
    "vignette": ["method": "radial gradient multiply (sRGB-encoded), smooth", "inner_radius_half_diag": VIG_INNER, "outer_radius_half_diag": VIG_OUTER, "edge_gain": VIG_EDGE_GAIN],
    "grain": ["source": "CIRandomGenerator (deterministic) offset by SplitMix64(seed, global frame index)",
              "type": "monochrome additive zero-mean (sRGB-encoded), uniform noise pre-blurred", "amplitude": GRAIN_AMP, "pre_blur_sigma_px": GRAIN_SOFTEN, "approx_std_srgb_code_values_8bit": 4, "scale": GRAIN_SCALE, "animated_per_output_frame": true],
]
let OUT_W = 1280, OUT_H = 720, FPS: Int32 = 24

// MARK: - Helpers

struct Fail: Error { let code: Int32; let msg: String }
func die(_ code: Int32, _ msg: String) -> Never { fputs("finish_anime: \(msg)\n", stderr); exit(code) }

func sha256(_ url: URL) -> String {
    guard let h = try? FileHandle(forReadingFrom: url) else { return "unreadable" }
    defer { try? h.close() }
    var hasher = SHA256()
    while true { let d = h.readData(ofLength: 8 << 20); if d.isEmpty { break }; hasher.update(data: d) }
    return hasher.finalize().map { String(format: "%02x", $0) }.joined()
}

struct SplitMix64 { var s: UInt64
    mutating func next() -> UInt64 { s &+= 0x9E3779B97F4A7C15; var z = s
        z = (z ^ (z >> 30)) &* 0xBF58476D1CE4E5B9; z = (z ^ (z >> 27)) &* 0x94D049BB133111EB; return z ^ (z >> 31) } }

// MARK: - Arguments

var args = Array(CommandLine.arguments.dropFirst())
var outArg: String?, audioArg = "audio/opening-rain/rain-preview.wav", rootArg = FileManager.default.currentDirectoryPath
var letterbox: Double?, seed: UInt64 = 20261005, reportArg: String?, contactArg: String?, clipArgs: [String] = []
var tierArg: String?, videoModelArg: String?, modelFolderArg: String?
while !args.isEmpty {
    let a = args.removeFirst()
    func val() -> String { guard !args.isEmpty else { die(64, "missing value for \(a)") }; return args.removeFirst() }
    switch a {
    case "--out": outArg = val()
    case "--audio": audioArg = val()
    case "--project-root": rootArg = val()
    case "--letterbox": guard let r = Double(val()), r > 16.0 / 9.0 else { die(64, "--letterbox needs a ratio > 1.778") }; letterbox = r
    case "--seed": guard let s = UInt64(val()) else { die(64, "bad --seed") }; seed = s
    case "--report": reportArg = val()
    case "--contact": contactArg = val()
    case "--tier": tierArg = val()
    case "--video-model": videoModelArg = val()
    case "--model-folder": modelFolderArg = val()
    case "--clips-file":
        let path = val()
        guard let txt = try? String(contentsOfFile: path, encoding: .utf8) else { die(2, "cannot read \(path)") }
        clipArgs += txt.split(separator: "\n").map { $0.trimmingCharacters(in: .whitespaces) }.filter { !$0.isEmpty && !$0.hasPrefix("#") }
    case "-h", "--help": print("usage: finish_anime --out OUT.mp4 [--audio WAV] [--letterbox 2.39] [--project-root DIR] [--seed N] [--report R] [--contact C] [--tier T] [--video-model ID] [--model-folder F] [--clips-file F] clips..."); exit(0)
    default: if a.hasPrefix("--") { die(64, "unknown option \(a)") }; clipArgs.append(a)
    }
}
guard let outArg else { die(64, "--out is required") }
guard !clipArgs.isEmpty else { die(64, "no clips given") }
let root = URL(fileURLWithPath: rootArg, isDirectory: true)
func resolve(_ p: String) -> URL { URL(fileURLWithPath: p, relativeTo: root).standardizedFileURL }
let outURL = resolve(outArg)
let stem = outURL.deletingPathExtension().lastPathComponent, dir = outURL.deletingLastPathComponent()
let lbURL: URL? = letterbox.map { _ in dir.appendingPathComponent("\(stem)-letterbox.mp4") }
let reportURL = reportArg.map(resolve) ?? dir.appendingPathComponent("\(stem).report.json")
let contactURL = contactArg.map(resolve) ?? dir.appendingPathComponent("\(stem)-contact.png")
let audioURL = resolve(audioArg)
let clipURLs = clipArgs.map(resolve)
let fm = FileManager.default
for u in [outURL, reportURL, contactURL] + (lbURL.map { [$0] } ?? []) where fm.fileExists(atPath: u.path) {
    die(2, "refuse to overwrite existing \(u.path)")
}
for u in clipURLs + [audioURL] where !fm.fileExists(atPath: u.path) { die(2, "missing input \(u.path)") }

func rel(_ u: URL) -> String { u.path.hasPrefix(root.path + "/") ? String(u.path.dropFirst(root.path.count + 1)) : u.path }
func shotId(_ u: URL) -> String {   // .../<shot_dir>/attempt-NN/<file>.mp4
    let parts = u.pathComponents
    if parts.count >= 3, parts[parts.count - 2].hasPrefix("attempt-") { return parts[parts.count - 3] }
    return u.deletingPathExtension().lastPathComponent
}
func attempt(_ u: URL) -> String? { let p = u.pathComponents; return p.count >= 2 && p[p.count - 2].hasPrefix("attempt-") ? p[p.count - 2] : nil }

// MARK: - Probe clips

struct Clip { let url: URL; let id: String; let duration: Double; let srcFps: Float; let outFrames: Int; let w: Int; let h: Int }
var clips: [Clip] = []
for u in clipURLs {
    let asset = AVURLAsset(url: u, options: [AVURLAssetPreferPreciseDurationAndTimingKey: true])
    guard let t = asset.tracks(withMediaType: .video).first else { die(2, "no video track in \(u.path)") }
    let d = CMTimeGetSeconds(asset.duration)
    let n = Int((d * Double(FPS)).rounded())
    guard n > 0 else { die(2, "empty clip \(u.path)") }
    clips.append(Clip(url: u, id: shotId(u), duration: d, srcFps: t.nominalFrameRate, outFrames: n,
                      w: Int(t.naturalSize.width), h: Int(t.naturalSize.height)))
}
let totalFrames = clips.reduce(0) { $0 + $1.outFrames }
let totalSeconds = Double(totalFrames) / Double(FPS)
let audioAsset = AVURLAsset(url: audioURL)
guard let audioTrackFound = audioAsset.tracks(withMediaType: .audio).first else { die(2, "no audio track in \(audioURL.path)") }
let audioTrack: AVAssetTrack = audioTrackFound
let audioSeconds = CMTimeGetSeconds(audioAsset.duration)
var warnings: [String] = []
if audioSeconds + 0.02 < totalSeconds { warnings.append("audio (\(audioSeconds) s) shorter than picture (\(totalSeconds) s); tail is silent") }
for c in clips where c.w != OUT_W || c.h != OUT_H { warnings.append("\(c.id) is \(c.w)x\(c.h); scaled to fit \(OUT_W)x\(OUT_H)") }

// MARK: - CoreImage pipeline

let ctx = CIContext(options: [.workingColorSpace: CGColorSpace(name: CGColorSpace.extendedLinearSRGB)!, .cacheIntermediates: false])
let cs709 = CGColorSpace(name: CGColorSpace.itur_709)!
let extent = CGRect(x: 0, y: 0, width: OUT_W, height: OUT_H)
let noiseBase = CIFilter.randomGenerator().outputImage!.applyingGaussianBlur(sigma: Double(GRAIN_SOFTEN))
let lbActiveH: Int = letterbox.map { r in Int((Double(OUT_W) / r / 2).rounded()) * 2 } ?? OUT_H
let lbBar = (OUT_H - lbActiveH) / 2
let black = CIImage(color: .black)
let barsImage: CIImage = black.cropped(to: CGRect(x: 0, y: 0, width: OUT_W, height: lbBar))
    .composited(over: black.cropped(to: CGRect(x: 0, y: OUT_H - lbBar, width: OUT_W, height: lbBar)))

// Zero-mean monochrome grain added to sRGB-encoded values (alpha untouched).
let grainKernel = CIColorKernel(source: "kernel vec4 grain(__sample s, __sample n, float a) { return vec4(s.rgb + (n.r - 0.5) * a, s.a); }")!
let diag = hypot(CGFloat(OUT_W), CGFloat(OUT_H))
let vignetteMask: CIImage = {
    let f = CIFilter.radialGradient()
    f.center = CGPoint(x: CGFloat(OUT_W) / 2, y: CGFloat(OUT_H) / 2)
    f.radius0 = Float(VIG_INNER * diag / 2); f.radius1 = Float(VIG_OUTER * diag / 2)
    f.color0 = CIColor(red: 1, green: 1, blue: 1); f.color1 = CIColor(red: VIG_EDGE_GAIN, green: VIG_EDGE_GAIN, blue: VIG_EDGE_GAIN)
    return f.outputImage!.cropped(to: extent)
}()

func finish(_ pb: CVPixelBuffer, globalFrame: Int) -> CIImage {
    var img = CIImage(cvPixelBuffer: pb)
    if img.extent.size != extent.size {
        let s = min(CGFloat(OUT_W) / img.extent.width, CGFloat(OUT_H) / img.extent.height)
        img = img.transformed(by: CGAffineTransform(scaleX: s, y: s)).cropped(to: extent)
    }
    // 1. Bloom: per-channel highlights above threshold, blurred, mixed additively (pre-grade).
    let hi = CIFilter.colorMatrix(); hi.inputImage = img
    let g = BLOOM_GAIN, th = BLOOM_THRESHOLD
    hi.rVector = CIVector(x: g, y: 0, z: 0, w: 0); hi.gVector = CIVector(x: 0, y: g, z: 0, w: 0)
    hi.bVector = CIVector(x: 0, y: 0, z: g, w: 0); hi.biasVector = CIVector(x: -g * th, y: -g * th, z: -g * th, w: 0)
    let clamp = CIFilter.colorClamp(); clamp.inputImage = hi.outputImage
    clamp.minComponents = CIVector(x: 0, y: 0, z: 0, w: 1); clamp.maxComponents = CIVector(x: 1, y: 1, z: 1, w: 1)
    let blur = CIFilter.gaussianBlur(); blur.inputImage = clamp.outputImage!.clampedToExtent(); blur.radius = Float(BLOOM_RADIUS)
    let mix = CIFilter.colorMatrix(); mix.inputImage = blur.outputImage!.cropped(to: extent)
    let m = BLOOM_MIX
    mix.rVector = CIVector(x: m, y: 0, z: 0, w: 0); mix.gVector = CIVector(x: 0, y: m, z: 0, w: 0)
    mix.bVector = CIVector(x: 0, y: 0, z: m, w: 0); mix.aVector = CIVector(x: 0, y: 0, z: 0, w: 0)
    mix.biasVector = CIVector(x: 0, y: 0, z: 0, w: 0)
    img = mix.outputImage!.applyingFilter("CIAdditionCompositing", parameters: [kCIInputBackgroundImageKey: img]).cropped(to: extent)
    // 2. Night grade (same parameters for all clips). Exposure in linear light; everything after
    //    is done on sRGB-encoded values (explicit sandwich) so curve points are perceptual.
    img = img.applyingFilter("CIExposureAdjust", parameters: [kCIInputEVKey: EXPOSURE_EV])
    img = img.applyingFilter("CILinearToSRGBToneCurve")
    img = img.applyingFilter("CIColorControls", parameters: [kCIInputSaturationKey: SATURATION, kCIInputContrastKey: CONTRAST, kCIInputBrightnessKey: 0.0])
    let tc = CIFilter.toneCurve(); tc.inputImage = img
    tc.point0 = CURVE[0]; tc.point1 = CURVE[1]; tc.point2 = CURVE[2]; tc.point3 = CURVE[3]; tc.point4 = CURVE[4]
    img = tc.outputImage!
    let tint = CIFilter.colorMatrix(); tint.inputImage = img
    tint.rVector = CIVector(x: TINT_GAIN[0], y: 0, z: 0, w: 0); tint.gVector = CIVector(x: 0, y: TINT_GAIN[1], z: 0, w: 0)
    tint.bVector = CIVector(x: 0, y: 0, z: TINT_GAIN[2], w: 0); tint.biasVector = CIVector(x: TINT_BIAS[0], y: TINT_BIAS[1], z: TINT_BIAS[2], w: 0)
    img = tint.outputImage!
    // 3. Vignette (very light).
    img = vignetteMask.applyingFilter("CIMultiplyCompositing", parameters: [kCIInputBackgroundImageKey: img]).cropped(to: extent)
    // 4. Grain: deterministic softened noise, seeded offset per global output frame, monochrome, additive (zero-mean).
    var rng = SplitMix64(s: seed &+ UInt64(globalFrame) &* 0x9E37)
    let ox = CGFloat(rng.next() % 4096), oy = CGFloat(rng.next() % 4096)
    let n = noiseBase.transformed(by: CGAffineTransform(translationX: -ox, y: -oy))
        .transformed(by: CGAffineTransform(scaleX: GRAIN_SCALE, y: GRAIN_SCALE)).cropped(to: extent)
    let a = GRAIN_AMP
    img = grainKernel.apply(extent: extent, arguments: [img, n, a])!
    return img.applyingFilter("CISRGBToneCurveToLinear")
}

// MARK: - Writers

final class Out {
    let url: URL, partial: URL, writer: AVAssetWriter, v: AVAssetWriterInput, a: AVAssetWriterInput
    let adaptor: AVAssetWriterInputPixelBufferAdaptor, aReader: AVAssetReader, aOut: AVAssetReaderTrackOutput
    var audioDone = false
    init(_ url: URL) throws {
        self.url = url
        partial = url.deletingLastPathComponent().appendingPathComponent(".\(url.lastPathComponent).partial.mp4")
        try? FileManager.default.removeItem(at: partial)
        writer = try AVAssetWriter(outputURL: partial, fileType: .mp4)
        writer.shouldOptimizeForNetworkUse = false
        v = AVAssetWriterInput(mediaType: .video, outputSettings: [
            AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: OUT_W, AVVideoHeightKey: OUT_H,
            AVVideoColorPropertiesKey: [AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
                                        AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
                                        AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2],
            AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 10_000_000,
                                              AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
                                              AVVideoExpectedSourceFrameRateKey: Int(FPS),
                                              AVVideoMaxKeyFrameIntervalKey: Int(FPS) * 2,
                                              AVVideoAllowFrameReorderingKey: false]])
        v.expectsMediaDataInRealTime = false
        adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: v, sourcePixelBufferAttributes: [
            kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
            kCVPixelBufferWidthKey as String: OUT_W, kCVPixelBufferHeightKey as String: OUT_H,
            kCVPixelBufferIOSurfacePropertiesKey as String: [:]])
        var layout = AudioChannelLayout(); layout.mChannelLayoutTag = kAudioChannelLayoutTag_Stereo
        a = AVAssetWriterInput(mediaType: .audio, outputSettings: [
            AVFormatIDKey: kAudioFormatMPEG4AAC, AVSampleRateKey: 48000, AVNumberOfChannelsKey: 2, AVEncoderBitRateKey: 192_000,
            AVChannelLayoutKey: Data(bytes: &layout, count: MemoryLayout<AudioChannelLayout>.size)])
        a.expectsMediaDataInRealTime = false
        writer.add(v); writer.add(a)
        aReader = try AVAssetReader(asset: audioAsset)
        aReader.timeRange = CMTimeRange(start: .zero, duration: CMTime(value: Int64(totalFrames), timescale: FPS))
        aOut = AVAssetReaderTrackOutput(track: audioTrack, outputSettings: [
            AVFormatIDKey: kAudioFormatLinearPCM, AVSampleRateKey: 48000, AVNumberOfChannelsKey: 2,
            AVLinearPCMBitDepthKey: 16, AVLinearPCMIsFloatKey: false, AVLinearPCMIsBigEndianKey: false, AVLinearPCMIsNonInterleaved: false])
        aReader.add(aOut)
        guard aReader.startReading(), writer.startWriting() else { throw Fail(code: 3, msg: "cannot start writer/audio for \(url.lastPathComponent): \(String(describing: writer.error ?? aReader.error))") }
        writer.startSession(atSourceTime: .zero)
    }
    func pumpAudio() throws -> Bool {
        var progressed = false
        while !audioDone && a.isReadyForMoreMediaData {
            if let s = aOut.copyNextSampleBuffer() { guard a.append(s) else { throw Fail(code: 3, msg: "audio append failed") } }
            else { a.markAsFinished(); audioDone = true }
            progressed = true
        }
        return progressed
    }
}

var outs: [(Out, Bool)] = []   // (writer, isLetterbox)
func cleanup() { for (o, _) in outs { o.writer.cancelWriting(); try? fm.removeItem(at: o.partial) } }
do {
    try fm.createDirectory(at: dir, withIntermediateDirectories: true)
    outs.append((try Out(outURL), false))
    if let lbURL { outs.append((try Out(lbURL), true)) }
} catch let e as Fail { cleanup(); die(e.code, e.msg) } catch { cleanup(); die(3, "\(error)") }

// MARK: - Render loop

let bgra: [String: Any] = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
                           kCVPixelBufferIOSurfacePropertiesKey as String: [:]]
var clipReports: [[String: Any]] = []
var contactImages: [(String, Double, CGImage)] = []
var global = 0
let t0 = Date()

func waitAndAppend(_ img: CIImage, _ frame: Int) throws {
    for (o, isLB) in outs {
        var lastProgress = Date()
        while !o.v.isReadyForMoreMediaData {
            if try o.pumpAudio() { lastProgress = Date() } else { usleep(500) }
            guard o.writer.status == .writing, Date().timeIntervalSince(lastProgress) < 60 else {
                throw Fail(code: 3, msg: "writer stalled: \(String(describing: o.writer.error))") }
        }
        var pb: CVPixelBuffer?
        guard let pool = o.adaptor.pixelBufferPool, CVPixelBufferPoolCreatePixelBuffer(nil, pool, &pb) == kCVReturnSuccess, let dst = pb
        else { throw Fail(code: 3, msg: "pixel buffer allocation failed") }
        let frameImg = isLB ? barsImage.composited(over: img) : img
        ctx.render(frameImg, to: dst, bounds: extent, colorSpace: cs709)
        guard o.adaptor.append(dst, withPresentationTime: CMTime(value: Int64(frame), timescale: FPS)) else {
            throw Fail(code: 3, msg: "video append failed at \(frame): \(String(describing: o.writer.error))") }
        _ = try o.pumpAudio()
    }
}

do {
    var cursor = 0
    for c in clips {
        let asset = AVURLAsset(url: c.url, options: [AVURLAssetPreferPreciseDurationAndTimingKey: true])
        let reader = try AVAssetReader(asset: asset)
        let vtrack = asset.tracks(withMediaType: .video)[0]
        let trackStart = CMTimeGetSeconds(vtrack.timeRange.start)
        let output = AVAssetReaderTrackOutput(track: vtrack, outputSettings: bgra)
        output.alwaysCopiesSampleData = false
        reader.add(output)
        guard reader.startReading() else { throw Fail(code: 3, msg: "cannot decode \(c.url.path)") }
        var cur: (pts: Double, idx: Int, pb: CVPixelBuffer)?
        var pending: (pts: Double, pb: CVPixelBuffer)?
        var srcIndex = -1, decoded = 0
        var usedSource: [Int] = []
        let mid = c.outFrames / 2 / 2 * 2   // even frame = start of a held pair, centred
        for i in 0..<c.outFrames {
            let holdT = Double(i / 2 * 2) / Double(FPS) + 1e-4
            // advance to the latest source frame with pts <= holdT (on twos: sampling, no interpolation)
            while true {
                if pending == nil, let s = output.copyNextSampleBuffer() {
                    if CMSampleBufferGetNumSamples(s) > 0, let ib = CMSampleBufferGetImageBuffer(s) {
                        pending = (CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(s)), ib); decoded += 1
                    }
                    continue
                }
                guard let p = pending, cur == nil || p.pts - trackStart <= holdT else { break }
                srcIndex += 1; cur = (p.pts, srcIndex, p.pb); pending = nil
            }
            guard let frame = cur else { throw Fail(code: 3, msg: "no decodable frame in \(c.url.path)") }
            if i % 2 == 0 { usedSource.append(frame.idx) }
            let img = finish(frame.pb, globalFrame: global)
            if i == mid, let cg = ctx.createCGImage(img, from: extent, format: .RGBA8, colorSpace: cs709) {
                contactImages.append((c.id, Double(i) / Double(FPS), cg))
            }
            try waitAndAppend(img, global)
            global += 1
        }
        reader.cancelReading()
        clipReports.append(["shot_id": c.id, "source": rel(c.url), "attempt": attempt(c.url).map { $0 as Any } ?? NSNull(),
                            "source_sha256": sha256(c.url), "source_duration_s": c.duration, "source_nominal_fps": c.srcFps,
                            "source_frames_decoded_until_last_hold": decoded,
                            "start_frame": cursor, "end_frame_exclusive": cursor + c.outFrames, "output_frames": c.outFrames,
                            "start_s": Double(cursor) / Double(FPS), "duration_s": Double(c.outFrames) / Double(FPS),
                            "held_images": usedSource.count, "source_indices_sampled": usedSource,
                            "contact_frame_s_in_clip": Double(mid) / Double(FPS), "transition_in": cursor == 0 ? "start" : "hard_cut"])
        cursor += c.outFrames
        fputs("finish_anime: \(c.id) done (\(cursor)/\(totalFrames) frames, \(Int(Date().timeIntervalSince(t0))) s)\n", stderr)
    }
    // finish audio + writers
    for (o, _) in outs {
        o.v.markAsFinished()
        var last = Date()
        while !o.audioDone {
            if try o.pumpAudio() { last = Date() } else { usleep(1000) }
            guard Date().timeIntervalSince(last) < 60 else { throw Fail(code: 3, msg: "audio stalled") }
        }
        o.writer.endSession(atSourceTime: CMTime(value: Int64(totalFrames), timescale: FPS))
        let sem = DispatchSemaphore(value: 0)
        o.writer.finishWriting { sem.signal() }
        guard sem.wait(timeout: .now() + 120) == .success, o.writer.status == .completed else {
            throw Fail(code: 3, msg: "finish failed: \(String(describing: o.writer.error))") }
    }
} catch let e as Fail { cleanup(); die(e.code, e.msg) } catch { cleanup(); die(3, "\(error)") }

// MARK: - Validate, publish, contact sheet, report

var outputsReport: [[String: Any]] = []
for (o, isLB) in outs {
    let r = AVURLAsset(url: o.partial, options: [AVURLAssetPreferPreciseDurationAndTimingKey: true])
    guard let vt = r.tracks(withMediaType: .video).first, let at = r.tracks(withMediaType: .audio).first,
          let vr = try? AVAssetReader(asset: r) else { cleanup(); die(3, "validation: tracks missing in \(o.url.lastPathComponent)") }
    let vo = AVAssetReaderTrackOutput(track: vt, outputSettings: nil); vr.add(vo); vr.startReading()
    var count = 0; while let s = vo.copyNextSampleBuffer() { count += CMSampleBufferGetNumSamples(s) }
    let dur = CMTimeGetSeconds(r.duration), adur = CMTimeGetSeconds(at.timeRange.duration)
    guard count == totalFrames, abs(dur - totalSeconds) < 0.05, Int(vt.naturalSize.width) == OUT_W, Int(vt.naturalSize.height) == OUT_H
    else { cleanup(); die(3, "validation failed for \(o.url.lastPathComponent): frames \(count) dur \(dur)") }
    do { try fm.moveItem(at: o.partial, to: o.url) } catch { cleanup(); die(3, "publish failed: \(error)") }
    var row: [String: Any] = ["path": rel(o.url), "sha256": sha256(o.url), "frames": count, "duration_s": dur,
                              "audio_duration_s": adur, "fps": vt.nominalFrameRate, "width": OUT_W, "height": OUT_H,
                              "video": "H.264 High, Rec.709 tags, 10 Mb/s", "audio": "AAC-LC 48 kHz stereo 192 kb/s",
                              "letterbox": isLB]
    if isLB { row["letterbox_ratio"] = letterbox!; row["active_picture"] = [OUT_W, lbActiveH]; row["bar_px_top_bottom"] = lbBar }
    outputsReport.append(row)
}

// contact sheet 3 columns, tiles 640x360 + caption band
let cols = 3, tw = 640, th = 360, cap = 28
let rows = (contactImages.count + cols - 1) / cols
let sw = cols * tw, sh = rows * (th + cap)
if let cg = CGContext(data: nil, width: sw, height: sh, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                      bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) {
    cg.setFillColor(CGColor(gray: 0.08, alpha: 1)); cg.fill(CGRect(x: 0, y: 0, width: sw, height: sh))
    let font = CTFontCreateWithName("Menlo" as CFString, 16, nil)
    for (k, (id, t, img)) in contactImages.enumerated() {
        let x = (k % cols) * tw, yTop = (k / cols) * (th + cap)
        let y = sh - yTop - th - cap
        cg.draw(img, in: CGRect(x: x, y: y + cap, width: tw, height: th))
        let label = "\(String(format: "%02d", k + 1))  \(id)  @\(String(format: "%.2f", t))s"
        let attr = NSAttributedString(string: label, attributes: [kCTFontAttributeName as NSAttributedString.Key: font,
                                                                  kCTForegroundColorAttributeName as NSAttributedString.Key: CGColor(gray: 0.9, alpha: 1)])
        cg.textPosition = CGPoint(x: x + 8, y: y + 8)
        CTLineDraw(CTLineCreateWithAttributedString(attr), cg)
    }
    if let sheet = cg.makeImage(), let dst = CGImageDestinationCreateWithURL(contactURL as CFURL, UTType.png.identifier as CFString, 1, nil) {
        CGImageDestinationAddImage(dst, sheet, nil); CGImageDestinationFinalize(dst)
    }
}

var audioManifest: Any = NSNull()
let mfURL = audioURL.deletingLastPathComponent().appendingPathComponent("manifest.json")
if let d = try? Data(contentsOf: mfURL), let j = try? JSONSerialization.jsonObject(with: d) as? [String: Any] {
    audioManifest = ["manifest": rel(mfURL), "label": j["label"] ?? NSNull(), "status": j["status"] ?? NSNull(),
                     "synthetic": j["synthetic"] ?? NSNull(), "ai_generated": j["ai_generated"] ?? NSNull(), "final_foley": j["final_foley"] ?? NSNull()]
}
let report: [String: Any] = [
    "tool": "tools/edit/finish_anime.swift", "created": ISO8601DateFormatter().string(from: Date()),
    "scope": "local_image_finishing_only_no_generation_no_spend_no_network",
    "cost": ["finishing_cost_usd": 0, "note": "Local CPU/GPU only (AVFoundation + CoreImage). Source clip generation cost is owned by their generation records; not restated here (unknown is not zero)."],
    "provenance": ["tier": tierArg.map { $0 as Any } ?? NSNull(), "video_model": videoModelArg.map { $0 as Any } ?? NSNull(),
                   "model_folder": modelFolderArg.map { $0 as Any } ?? NSNull(),
                   "no_rerender_no_tier_upgrade": true, "dialogue": "none (no TTS)", "music": "none"],
    "seed": seed, "parameters": P, "edit": ["transitions": "hard cuts", "fps": FPS, "total_frames": totalFrames, "total_duration_s": totalSeconds],
    "audio": ["path": rel(audioURL), "sha256": sha256(audioURL), "source_duration_s": audioSeconds, "laid_at_s": 0,
              "trimmed_to_s": min(audioSeconds, totalSeconds), "provenance": audioManifest,
              "note": "temporary bed; sound design to come"],
    "clips": clipReports, "outputs": outputsReport, "contact_sheet": rel(contactURL),
    "render_seconds": Date().timeIntervalSince(t0), "warnings": warnings]
do {
    let data = try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys])
    try data.write(to: reportURL)
} catch { die(3, "report write failed: \(error)") }
print("{\"ok\":true,\"frames\":\(totalFrames),\"duration_s\":\(totalSeconds),\"report\":\"\(rel(reportURL))\"}")
