/*
 * Copyright 2026 FloralDroid
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "config.h"

#if defined(FLORAL_FFMPEG_BACKEND_VAAPI) == defined(FLORAL_FFMPEG_BACKEND_V4L2_M2M)
#error "Select exactly one Floral FFmpeg backend"
#endif

#if defined(FLORAL_FFMPEG_BACKEND_V4L2_M2M)
#if !ARCH_AARCH64
#error "The V4L2 M2M profile must target AArch64"
#endif
#if !CONFIG_V4L2_M2M
#error "FloralDroid ARM64 FFmpeg requires the V4L2 M2M backend"
#endif
#else
#if !ARCH_X86_64
#error "The VAAPI profile must target x86_64"
#endif
#if !HAVE_VAAPI_DRM
#error "FloralDroid FFmpeg requires the VA-API DRM display backend"
#endif
#endif
