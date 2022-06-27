import * as toml from 'toml'
import * as fs from 'fs'

const PRODUCTION = 'PROD'
const DEVELOPMENT = 'DEV'
const MODES = [PRODUCTION, DEVELOPMENT]

function getMode() {
    let mode = undefined

    if (process.env.APP_MODE && MODES.includes(String(process.env.APP_MODE).toUpperCase())) {
        mode = String(process.env.APP_MODE).toUpperCase()
    }

    return mode
}

export function appConfig() {
    const mode = getMode()

    if (mode === DEVELOPMENT) {
        return toml.parse(fs.readFileSync('../config/dev.toml', 'utf-8'))
    }

    return toml.parse(fs.readFileSync('../config/prod.toml', 'utf-8'))
}

export function useSSL(sslConfig) {
    if (sslConfig.enable) {
        return {
            cert: sslConfig.cert,
            key: sslConfig.key
        }
    }

    return false
}
