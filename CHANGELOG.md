## v0.1.11 (2026-02-24)

### Fix

- redirect logging output from stdout to stderr

## [0.2.0](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/compare/v0.1.14...v0.2.0) (2026-11-05)


### Features

* add execute_jsx_file tool ([13dfad0](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/13dfad061140e010d83981f1879175bb8cac15bd))
* add list_actions and play_action tools ([b8a8d67](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/b8a8d6741bdd621ae79cc5cd4a2827a495e56f28))
* implement dynamic tool registration for MCP server ([b49df6d](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/b49df6df373389a4fb9b7b0027def27e89668849))
* signal unreadable document dimensions in document/info and open_document ([#92](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/issues/92)) ([b4db6b4](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/b4db6b4029fe7f76090068581d4f41a72f38da62))


### Bug Fixes

* **ci:** attach release assets to the right tag without clobbering notes ([0d94c99](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/0d94c99752552b737ceb942573f29b70d9c0f666))
* **ci:** attach release assets with gh instead of softprops ([f008314](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/f008314c0683ca63eb4b5fe2a3a88123d36fbdd3))
* **ci:** cut releases with GITHUB_TOKEN instead of an expired PAT ([a17a7ac](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/a17a7aca77337ebc9824e50d0bdce6c7eb947cd2))
* **ci:** drop package-name so release-please tags merged release PRs ([fa0ec37](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/fa0ec37367cc664dc3ca2df6d23aa025f6a2d4a7))
* **ci:** drop pull-requests permission from reusable publish workflow ([142fdd7](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/142fdd7a42ee0f4602dde8684850bbe956638ad5))
* **ci:** publish release outputs when called by Release Please ([f23dddd](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/f23ddddc2c9cd42da81a8608709080b48591a76f))
* correct mock paths in FastMCP initialization tests ([db20706](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/db207067da607a6172a2c59ebe4626a8a52b2273))
* **deps:** update dependency mcp to v1.10.1 ([32a3824](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/32a3824d16d89468fbffb9126e663aa4876208f5))
* **deps:** update dependency mcp to v1.7.0 ([f3495d8](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/f3495d835de838d22ba2fd4fac53ba02ac2443fa))
* **deps:** update dependency mcp to v1.7.1 ([5797d17](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/5797d17c14f1825ef73dcd7fb8d6cc284f96486a))
* **deps:** update dependency mcp to v1.9.1 ([0f01a0b](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/0f01a0b6483395c39c6181908a9d7cd0fd907fc9))
* **deps:** update dependency mcp to v1.9.3 ([5c983b1](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/5c983b183fd905f9b036d978fe7d4a815c840051))
* **deps:** update dependency mcp to v1.9.4 ([d6c637b](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/d6c637b43a6de9f0af4c695a5aaa4d2b90acddb2))
* **deps:** update dependency photoshop-python-api to v0.24.1 ([3f81087](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/3f81087530ea8ef67b5e4ca6923991f3bb8c0a2e))
* dispatch publish workflow as top-level run to fix PyPI attestation ([#89](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/issues/89)) ([ba68e54](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/ba68e54517cb8234bb10ec4425ce24ad0fc801f7))
* handle UnitValue and float document dimensions ([863af0a](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/863af0aaa7aae211423bd79bac88441444315750))
* judge script failures only on explicit success:false and drop fake success payload ([058c11e](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/058c11ee6954c2049609d0a820fa728567b42308))
* keep multi-line error messages valid JSON so failures stay failures ([3d12a44](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/3d12a4415dcc299481b6390e7aa3129f483de3fe))
* open_document opens the requested file ([fc2fe6f](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/fc2fe6fd2084adb678ea945d88e648f4972b8846))
* populate layers in get_active_document_info and add execute_jsx tool ([82de08d](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/82de08d0650726dee351a44e30219c7c909657de))
* redirect logging output from stdout to stderr ([8f88bd2](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/8f88bd267676077464b954c5da1db5216231b302))
* remove unsupported description and version parameters from FastMCP initialization ([4aa2945](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/4aa29457326188fd588e2d1e6dbcb204d050506f))
* route all diagnostic output away from the MCP stdio stream ([#87](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/issues/87)) ([ffe7cda](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/ffe7cda0be7ec4eb7e11116159467154afb91998))
* standardize executable name to photoshop-mcp-server ([cd1ac61](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/cd1ac61da8dca948ca945b90a7d478a026b1d91d))
* update PyPI publish workflow to use Linux runner ([469f08a](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/469f08a9fa96b9830dde3f9926413cf4e4c1c866))
* use PhotoshopApp instance in Action Manager ([95cd252](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/95cd2522d2766322399948f370f11048ee416d73))


### Documentation

* add GIF demo to README ([31ded19](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/31ded19a07832db553972f2f950aab889b75a1c8))
* add modern badges to README and create Chinese version ([7ec2b31](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/7ec2b31b84cae3ce58d5217be305e702f269eb99))
* add Python version specification in uvx args ([df03908](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/df0390872478fda4978d97d5e9a1d4be5ed2b2ee))
* improve README layout and add more AI prompt examples ([3934bc7](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/3934bc7c7afacbd4bbd9269efbf1250a27367684))
* update README with improved MCP configuration examples ([56fed8d](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/56fed8d5f94d3879e73dd1b6f52593cf9ba66662))
* update README with standard uvx configuration format ([c4ea3e5](https://github.com/MoebiusSt/photoshop-python-api-mcp-server/commit/c4ea3e5c682467b7982f327bf01959b64f489a53))

## [0.1.14](https://github.com/loonghao/photoshop-python-api-mcp-server/compare/v0.1.13...v0.1.14) (2026-10-13)


### Bug Fixes

* route all diagnostic output away from the MCP stdio stream ([#87](https://github.com/loonghao/photoshop-python-api-mcp-server/issues/87)) ([ffe7cda](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/ffe7cda0be7ec4eb7e11116159467154afb91998))

## [0.1.13](https://github.com/loonghao/photoshop-python-api-mcp-server/compare/v0.1.12...v0.1.13) (2026-09-28)


### Bug Fixes

* **ci:** attach release assets to the right tag without clobbering notes ([0d94c99](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/0d94c99752552b737ceb942573f29b70d9c0f666))
* **ci:** attach release assets with gh instead of softprops ([f008314](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/f008314c0683ca63eb4b5fe2a3a88123d36fbdd3))
* **ci:** drop package-name so release-please tags merged release PRs ([fa0ec37](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/fa0ec37367cc664dc3ca2df6d23aa025f6a2d4a7))
* **ci:** publish release outputs when called by Release Please ([f23dddd](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/f23ddddc2c9cd42da81a8608709080b48591a76f))
* handle UnitValue and float document dimensions ([863af0a](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/863af0aaa7aae211423bd79bac88441444315750))
* register and document the execute_jsx tool ([8dc41d5](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/8dc41d585a16470d6d2e8ba29c1b32fb88c74dc9))

## [0.1.12](https://github.com/loonghao/photoshop-python-api-mcp-server/compare/v0.1.11...v0.1.12) (2026-09-28)


### Bug Fixes

* **ci:** cut releases with GITHUB_TOKEN instead of an expired PAT ([a17a7ac](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/a17a7aca77337ebc9824e50d0bdce6c7eb947cd2))
* **ci:** drop pull-requests permission from reusable publish workflow ([142fdd7](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/142fdd7a42ee0f4602dde8684850bbe956638ad5))
* populate layers in get_active_document_info and add execute_jsx tool ([82de08d](https://github.com/loonghao/photoshop-python-api-mcp-server/commit/82de08d0650726dee351a44e30219c7c909657de))

## v0.1.10 (2025-10-17)

### Fix

- correct mock paths in FastMCP initialization tests
- remove unsupported description and version parameters from FastMCP initialization

## v0.1.9 (2025-06-30)

### Fix

- **deps**: update dependency mcp to v1.10.1

## v0.1.8 (2025-06-18)

### Fix

- **deps**: update dependency mcp to v1.9.4

## v0.1.7 (2025-06-07)

### Fix

- **deps**: update dependency mcp to v1.9.3

## v0.1.6 (2025-05-26)

### Fix

- **deps**: update dependency mcp to v1.9.1

## v0.1.5 (2025-05-07)

### Fix

- **deps**: update dependency mcp to v1.7.1

## v0.1.4 (2025-05-07)

### Fix

- **deps**: update dependency photoshop-python-api to v0.24.1

## v0.1.3 (2025-05-02)

### Fix

- **deps**: update dependency mcp to v1.7.0

## v0.1.2 (2025-04-11)

### Fix

- standardize executable name to photoshop-mcp-server

## v0.1.1 (2025-04-11)

### Fix

- update PyPI publish workflow to use Linux runner

## v0.1.0 (2025-04-11)

### Feat

- implement dynamic tool registration for MCP server

### Fix

- use PhotoshopApp instance in Action Manager
